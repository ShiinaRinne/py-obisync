from sqlalchemy import Column, Integer, Text

from ..db import Base


class User(Base):
    __tablename__ = "users"
    email = Column(Text, nullable=False, primary_key=True)
    password = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    license = Column(Text, nullable=False)


class Vault(Base):
    __tablename__ = "vaults"
    id = Column(Text, primary_key=True)
    user_email = Column(Text, nullable=False)
    created = Column(Integer, nullable=False)
    host = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    salt = Column(Text, nullable=False)
    size = Column(Integer, default=0)
    version = Column(Integer, nullable=False, default=0)
    keyhash = Column(Text, nullable=False)


class Share(Base):
    __tablename__ = "shares"
    uid = Column(Text, primary_key=True)
    email = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    vault_id = Column(Text, nullable=False)
    accepted = Column(Integer, nullable=False, default=1)
