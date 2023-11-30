import uuid
import time
import bcrypt
from typing import List
from sqlalchemy.orm import Session

from obsync.utils import MakeKeyHash
from obsync.config import config
from obsync.schemas import VaultInfo
from obsync.db import session_handler

from .models.vault import User, Vault, Share
from .exceptions import *


@session_handler
def share_vault_invite(
    email: str, name: str, vault_id: str, session: Session
) -> None:
    new_share = Share(uid=str(uuid.uuid4()), email=email, name=name, vault_id=vault_id)

    session.add(new_share)
    session.commit()


@session_handler
def share_vault_revoke(
    shareUID: str, vault_id: str, email: str, session: Session
) -> None:
    if shareUID != "":
        session.query(Share).filter(Share.uid == shareUID).delete()
    else:
        session.query(Share).filter(
            Share.vault_id == vault_id, Share.email == email
        ).delete()
    session.commit()


@session_handler
def get_vault_shares(vault_id: str, session: Session) -> List[Share]:
    shares = session.query(Share).filter(Share.vault_id == vault_id).all()
    return shares


@session_handler
def get_shared_vaults(email: str, session: Session) -> List[VaultInfo]:
    vaults = (
        session.query(Vault)
        .join(Share, Vault.id == Share.vault_id)
        .filter(Share.email == email)
        .all()
    )
    return [
        VaultInfo(
            id=vault.id,
            created=vault.created,
            host=vault.host,
            name=vault.name,
            password=vault.password,
            salt=vault.salt,
            size=vault.size,
        )
        for vault in vaults
    ]


@session_handler
def has_access_to_vault(vault_id: str, email: str, session: Session) -> bool:
    row = (
        session.query(Vault)
        .filter(Vault.id == vault_id, Vault.user_email == email)
        .first()
    )
    return row is not None


@session_handler
def is_vault_owner(vault_id: str, email: str, session: Session) -> bool:
    row = (
        session.query(Vault)
        .filter(Vault.id == vault_id, Vault.user_email == email)
        .first()
    )
    return row is not None


@session_handler
def new_user(email: str, password: str, name: str, session: Session) -> None:
    hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    new_user = User(name=name, email=email, password=hash.decode("utf-8"), license="")
    session.add(new_user)
    session.commit()


@session_handler
def user_info(email: str, session: Session) -> User:
    user = session.query(User).filter(User.email == email).first()
    return user


@session_handler
def login(email: str, password: str, session: Session) -> User:
    user = session.query(User).filter(User.email == email).first()
    if user is None or not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise SigninException(
            email, "Invalid username or password"
        )  # write into one exception
    return user


@session_handler
def delete_user(email: str, session: Session) -> None:
    session.query(User).filter(User.email == email).delete()
    session.commit()


@session_handler
def new_vault(
    name: str,
    email: str,
    password: str,
    salt: str,
    keyhash: str,
    session: Session,
) -> VaultInfo:
    if keyhash == "" and password == "":
        raise ValueError("password and keyhash cannot both be empty")

    if keyhash == "": keyhash = MakeKeyHash(password, salt)
        
    vault = Vault(
        id=str(uuid.uuid4()),
        user_email=email,
        created=int(time.time()) * 1000,
        host=config.Host,
        name=name,
        password=password,
        salt=salt,
        keyhash=keyhash,
        size=config.MaxStorageBytes,
    )
    session.add(vault)
    session.commit()
    
    return VaultInfo(
        id=vault.id,
        created=vault.created,
        host=vault.host,
        name=vault.name,
        password=vault.password,
        salt=vault.salt,
        size=vault.size,
        keyhash=vault.keyhash,
    )


@session_handler
def delete_vault(vault_id: str, email: str, session: Session) -> None:
    session.query(Vault).filter(
        Vault.id == vault_id, Vault.user_email == email
    ).delete()
    session.commit()


@session_handler
def get_vault(vault_id: str, keyhash: str, session: Session) -> Vault:
    vault = session.query(Vault).filter(Vault.id == vault_id).first()
    if vault.keyhash != keyhash:
        raise Exception("keyhash not match")
    return VaultInfo(
        id=vault.id,
        created=vault.created,
        host=vault.host,
        name=vault.name,
        password=vault.password,
        salt=vault.salt,
        size=vault.size,
        version=vault.version,
    )


@session_handler
def set_vault_version(id: str, ver: int, session: Session) -> None:
    session.query(Vault).filter(Vault.id == id).update({Vault.version: ver})
    session.commit()


@session_handler
def get_vaults(email: str, session: Session) -> List[VaultInfo]:
    vaults = session.query(Vault).filter(Vault.user_email == email).all()
    return [
        VaultInfo(
            id=vault.id,
            created=vault.created,
            host=vault.host,
            name=vault.name,
            password=vault.password,
            salt=vault.salt,
            size=vault.size,
        )
        for vault in vaults
    ]
