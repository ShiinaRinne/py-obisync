from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from obsync.schemas.vaultfiles import FileResponse, HistoryFileResponse, FileInfo
from obsync.logger import logger
from obsync.db import session_handler
from obsync.utils import milisec

from .models.vaultfiles import File


@session_handler
def snap_shot(vault_id: str, session: Session) -> None:
    session.query(File).filter(File.vault_id == vault_id, File.newest == True).update(
        {"is_snapshot": True}
    )
    session.query(File).filter(
        File.vault_id == vault_id, File.is_snapshot == False
    ).delete()
    session.query(File).filter(
        File.vault_id == vault_id, File.size != 0, File.data == None
    ).delete()
    session.commit()


@session_handler
def restore_file(uid: int, session: Session) -> FileResponse:
    file = session.query(File.uid, File.path, File.hash, File.extension, File.size, File.created, File.modified, File.folder, File.deleted).filter(File.uid == uid).first()
    
    session.query(File).filter(File.uid == uid).update(
        {"deleted": False, "newest": True}
    )
    session.commit()
    # TODO: check if this is correct
    session.query(File).filter(File.path == file.path, File.deleted == False).update(
        {"newest": False}
    )
    return FileResponse(
        uid = file.uid,
        hash= file.hash,
        path= file.path,
        extension= file.extension,
        size = file.size,
        created = file.created,
        modified = file.modified,
        folder = file.folder,
        deleted = file.deleted,
        op = "push",
    )


@session_handler
def get_vault_size(vault_id: str, session: Session) -> int:
    size = (
        session.query(func.coalesce(func.sum(File.size), 0))
        .filter(File.vault_id == vault_id)
        .scalar()
    )
    return size


@session_handler
def get_vault_files(vault_id: str, session: Session) -> List[FileInfo]:
    files = (
        session.query(File)
        .filter(File.vault_id == vault_id, File.deleted == False, File.newest == True)
        .all()
    )
    return [
        FileInfo(
            uid=file.uid,
            vault_id=file.vault_id,
            hash=file.hash,
            path=file.path,
            extension=file.extension,
            size=file.size,
            created=file.created,
            modified=file.modified,
            folder=file.folder,
            deleted=file.deleted,
            data=file.data,
            newest=file.newest,
            is_snapshot=file.is_snapshot,
        )
        for file in files
    ]


@session_handler
def get_file(uid: int, session: Session) -> FileInfo:
    file:File = session.query(File.hash, File.size, File.data).filter(File.uid == uid).first()
    return FileInfo(
        hash=file.hash,
        size=file.size,
        data=file.data,
    )



@session_handler
def get_file_history(path: str, session: Session) -> List[HistoryFileResponse]:
    # err := db.Model(&File{}).Select("uid, path, size, modified, folder, deleted").Where("path = ?", path).Order("modified DESC").Find(&files).Error
    files = (
        session.query(File.uid, File.path, File.size, File.modified, File.folder, File.deleted).filter(File.path == path).order_by(File.modified.desc()).all()
    )
    history = [
        HistoryFileResponse(
            uid=file.uid,
            path=file.path,
            modified=file.modified,
            folder=file.folder,
            deleted=file.deleted,
            ts=file.modified,
        )
        for file in files
    ]
    return history


@session_handler
def get_deleted_files(session: Session) -> List[dict]:
    files = session.query(File).filter(File.deleted == True, File.newest == True).all()
    return [
        {
            "uid": file.uid,
            "modified": file.modified,
            "size": file.size,
            "path": file.path,
            "folder": file.folder,
            "deleted": file.deleted,
        }
        for file in files
    ]


@session_handler
def insert_metadata(file: File, session: Session) -> int:
    current_time = milisec()
    if file.created == 0:
        file.created = current_time
    if file.modified == 0:
        file.modified = current_time

    session.query(File).filter(File.path == file.path, File.newest == True).update(
        {"newest": False}
    )
    session.add(file)
    session.commit()
    return file.uid


@session_handler
def insert_data(uid: int, data: bytes, session: Session):
    session.query(File).filter(File.uid == uid).update({"data": data})
    session.commit()


@session_handler
def delete_vault_file(path: str, session: Session):
    session.query(File).filter(File.path == path).update(
        {"deleted": True, "is_snapshot": True}
    )
    session.commit()
