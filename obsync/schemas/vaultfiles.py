from pydantic import BaseModel
from typing import Optional, Any


class FileInfo(BaseModel):
    uid: Optional[int] = 0
    vault_id: Optional[str] = ""
    hash: Optional[str] = ""
    path: Optional[str] = ""
    extension: Optional[str] = ""
    size: Optional[int] = 0
    created: Optional[int] = 0
    modified: Optional[int] = 0
    folder: Optional[bool] = False
    deleted: Optional[bool] = False
    data: Optional[bytes] = None
    newest: Optional[bool] = False
    is_snapshot: Optional[bool] = False


class FileResponse(FileInfo):
    op: Optional[str] = ""


class HistoryFileResponse(FileInfo):
    ts: Optional[int]


class WSHandlerPullModel(BaseModel):
    uid: int


class WSHandlerPushModel(BaseModel):
    uid: Optional[int] = 0
    op: Optional[str] = ""
    path: Optional[str] = ""
    extension: Optional[str] = ""
    hash: Optional[str] = ""
    ctime: Optional[int] = 0
    mtime: Optional[int] = 0
    folder: Optional[bool] = False
    deleted: Optional[bool] = False
    size: Optional[int] = 0
    pieces: Optional[int] = 0


class WSHandlerHistoryModel(BaseModel):
    last: Optional[Any] = None
    path: Optional[str] = ""


class WSHandlerRestoreModel(BaseModel):
    uid: Optional[int] = 0
