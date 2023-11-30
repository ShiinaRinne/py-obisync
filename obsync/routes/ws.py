import json
from fastapi import WebSocket, APIRouter
from typing import Dict, Any
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from obsync.db import vault, vaultfiles
from obsync.utils import *
from obsync.schemas.vaultfiles import (
    WSHandlerPushModel,
    WSHandlerPullModel,
    WSHandlerHistoryModel,
    WSHandlerRestoreModel,
)


class ChannelManager:
    def __init__(self, clients: Dict[WebSocket, bool]):
        self.clients = clients

    def add_client(self, websocket: WebSocket):
        self.clients[websocket] = True

    def remove_client(self, websocket: WebSocket):
        if websocket in self.clients:
            del self.clients[websocket]

    def is_empty(self):
        return len(self.clients) == 0

    async def broadcast(self, data: Dict[str, Any]):
        for client in self.clients:
            await client.send_json(data)


class InitializationRequest(BaseModel):
    op: str
    token: str
    id: str
    keyhash: str
    version: Any
    initial: bool
    device: str



async def handle_message(
    ws: WebSocket,
    msg: str,
    connectedVault: vault.Vault,
    version: int,
    channels: Dict[str, ChannelManager],
    version_bumped,
):
    msg = json.loads(msg)
    match msg["op"]:
        case "size":
            size = vaultfiles.get_vault_size(connectedVault.id)
            await ws.send_json(
                {"res": "ok", "size": size, "limit": config.MaxStorageBytes}
            )

        case "pull":
            pull = WSHandlerPullModel(**msg)
            uid: int = utils.to_int(pull.uid)
            file = vaultfiles.get_file(uid)
            pieces = 0 if file.size == 0 else 1
            await ws.send_json({"hash": file.hash, "size": file.size, "pieces": pieces})
            if file.size != 0:
                await ws.send_bytes(file.data)

        case "push":
            metadata = WSHandlerPushModel(**msg)
            if metadata.deleted:
                vaultfiles.delete_vault_file(metadata.path)
                vaultUID = metadata.uid
            else:
                vaultUID = vaultfiles.insert_metadata(
                    vaultfiles.File(
                        vault_id=connectedVault.id,
                        path=metadata.path,
                        extension=metadata.extension,
                        hash=metadata.hash,
                        size=metadata.size,
                        created=metadata.ctime,
                        modified=metadata.mtime,
                        folder=metadata.folder,
                        deleted=metadata.deleted,
                    )
                )
            if metadata.size > 0:
                full_binary = b""
                for _ in range(metadata.pieces):
                    await ws.send_json({"res": "next"})
                    full_binary += await ws.receive_bytes()
                vaultfiles.insert_data(vaultUID, full_binary)
            metadata.uid = vaultUID
            await channels[connectedVault.id].broadcast(metadata.model_dump())
            if not version_bumped:
                vault.set_vault_version(connectedVault.id, version + 1)
                version_bumped = True
            await ws.send_json({"op": "ok"})

        case "history":
            history = WSHandlerHistoryModel(**msg)
            files = vaultfiles.get_file_history(history.path)
            files = [file.model_dump() for file in files]
            await ws.send_json({"items": files, "more": False})

        case "ping":
            await ws.send_json({"op": "pong"})

        case "deleted":
            files = vaultfiles.get_deleted_files()
            await ws.send_json({"items": files})

        case "restore":
            restore = WSHandlerRestoreModel(**msg)
            uid: int = utils.to_int(restore.uid)
            file = vaultfiles.restore_file(uid)
            await channels[connectedVault.id].broadcast(file.model_dump())
            await ws.send_json({"res": "ok"})

        case "_":
            pass



ws_router = APIRouter(tags=["ws"])
channels: Dict[str, ChannelManager] = {}

@ws_router.websocket("/")
@ws_router.websocket("/ws")
@ws_router.websocket("/ws.obsidian.md")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        msg: Dict = await ws.receive_text()
        connectionInfo = InitializationRequest(**json.loads(msg))
        # Validate token and key hash
        email = get_jwt_email(connectionInfo.token)

        connectedVault = vault.get_vault(connectionInfo.id, connectionInfo.keyhash)

        logger.info(f"{email} - {connectionInfo.device} connected")

        if not vault.has_access_to_vault(connectedVault.id, email):
            await ws.send_json({"error": "no access to vault"})
            logger.info(
                f"{email} - {connectionInfo.device} has no access to vault {connectedVault.id}"
            )
            return
        await ws.send_json({"res": "ok"})

        version = to_int(connectionInfo.version)

        if connectedVault.version > version:
            files = vaultfiles.get_vault_files(connectedVault.id)
            for file in files:
                await ws.send_json(
                    {
                        "op": "push",
                        "path": file.path,
                        "hash": file.hash,
                        "size": file.size,
                        "ctime": file.created,
                        "mtime": file.modified,
                        "folder": file.folder,
                        "deleted": file.deleted,
                        "device": "insignificantv5",
                        "uid": file.uid,
                    }
                )

        version_bumped = False
        await ws.send_json({"op": "ready", "version": connectedVault.version})

        vaultfiles.snap_shot(connectedVault.id)

        if connectedVault.version < version:
            vault.set_vault_version(connectedVault.id, version)

        if connectedVault.id not in channels:
            channels[connectedVault.id] = ChannelManager(
                clients={}
            )  # TODO: clients: make(map[*ws.Conn]bool),

        channel = channels[connectedVault.id]
        channel.add_client(ws)

        try:
            while True:
                msg: Dict = await ws.receive_text()
                await handle_message(
                    ws, msg, connectedVault, version, channels, version_bumped
                )
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")

            channel.remove_client(ws)
            if channel.is_empty():
                del channels[connectedVault.id]
        except Exception as e:
            logger.error(e)
            logger.error(e.__traceback__)
            await ws.send_json({"error": str(e)})
            await ws.send_json({"error": str(e.__traceback__)})
    except Exception as e:
        await ws.send_json({"error": str(e)})
    finally:
        try:
            await ws.close()
        except RuntimeError:  # NOTE: client has already disconnected
            pass
