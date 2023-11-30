from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    LargeBinary,
    ForeignKey,
    BigInteger,
    Text,
)

from ..db import Base


class File(Base):
    __tablename__ = "files"
    uid = Column(Integer, primary_key=True, autoincrement=True)
    vault_id = Column(Text)
    hash = Column(Text)
    path = Column(Text)
    extension = Column(Text)
    size = Column(Integer)
    created = Column(Integer)
    modified = Column(Integer)
    folder = Column(Boolean)
    deleted = Column(Boolean)
    data = Column(LargeBinary)
    newest = Column(Boolean, default=True)
    is_snapshot = Column(Boolean, default=False)
