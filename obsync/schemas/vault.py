from pydantic import BaseModel
from typing import Optional


class Vault(BaseModel):
    id: str
    user_email: str
    created: int
    host: str
    name: str
    oassword: str
    salt: str
    size: int
    version: int
    keyhash: str


class Share(BaseModel):
    uid: str
    email: str
    name: str
    vault_id: str
    accepted: bool


class User(BaseModel):
    name: str
    email: str
    password: str
    license: str


class ListVaultRequest(BaseModel):
    token: str


class DeleteVaultRequest(BaseModel):
    token: str
    vault_uid: str


class CreateVaultRequest(BaseModel):
    token: str
    name: str
    salt: Optional[str] = None
    keyhash: Optional[str] = None


class VaultInfo(BaseModel):
    id: str
    created: int
    host: str
    name: str
    password: str
    salt: Optional[str] = None
    size: int
    keyhash: Optional[str] = None
    version: int = 0


class AccessVaultRequest(BaseModel):
    host: str
    token: str
    vault_uid: str
    keyhash: str
