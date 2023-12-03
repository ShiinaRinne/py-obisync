from sqlalchemy import Column, Integer, Text

from ..db import Base


class Site (Base):
    __tablename__ = "sites"
    id = Column(Text, primary_key=True)
    host = Column(Text, nullable=False)
    created = Column(Integer, nullable=False)
    owner = Column(Text, nullable=False)
    slug = Column(Text, nullable=False)
    options = Column(Text, nullable=False, default="")
    size = Column(Integer, default=0)
    
class PublishFile (Base):
    __tablename__ = "publish_files"
    path = Column(Text, nullable=False, primary_key=True, unique=True)
    ctime = Column(Integer, nullable=False)
    hash = Column(Text, nullable=False)
    mtime = Column(Integer, nullable=False)
    size = Column(Integer, nullable=False)
    data = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    deleted = Column(Integer)