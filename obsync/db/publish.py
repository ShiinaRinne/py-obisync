import time
import uuid

from typing import List

from sqlalchemy.orm import Session

from obsync.config import config
from obsync.db import session_handler
from obsync.utils import milisec

from .models.publish import *


@session_handler
def get_file(siteID: str, path: str, session: Session = None) -> str | None:
    s = (
        session.query(PublishFile)
        .filter(PublishFile.slug == siteID, PublishFile.path == path)
        .first()
    )
    return s.data if s is not None else None


@session_handler
def new_file(file: PublishFile, session: Session = None) -> None:
    file.ctime = milisec()
    file.mtime = milisec()

    session.merge(file)
    session.commit()


@session_handler
def remove_file(siteID: str, path: str, session: Session) -> None:
    session.query(PublishFile).filter(
        PublishFile.slug == siteID, PublishFile.path == path
    ).delete()
    session.commit()


@session_handler
def create_site(owner: str, session: Session) -> Site:
    site = Site(
        id=str(uuid.uuid4()),
        # host=config.Host,
        # TODO: custom host
        host="https://publish.youngmoe.com",
        created=milisec(),
        owner=owner,
        slug=str(uuid.uuid4()),
    )
    session.add(site)
    session.commit()
    return site


@session_handler
def delete_site(siteID: str, session: Session) -> None:
    session.query(Site).filter(Site.id == siteID).delete()
    session.commit()


class SlugResponse:
    def __init__(self, id: str, host: str, slug: str):
        self.id = id
        self.host = host
        self.slug = slug


@session_handler
def get_slug(slug: str, session: Session = None) -> SlugResponse | None:
    site = session.query(Site).filter(Site.slug == slug).first()
    if site is None:
        return None
    return SlugResponse(site.id, site.host, site.slug)


@session_handler
def set_slug(slug: str, id: str, session: Session = None) -> None:
    session.query(Site).filter(Site.id == id).update({"slug": slug})
    session.commit()


@session_handler
def get_sites(userEmail: str, session: Session = None) -> List[Site]:
    return session.query(Site).filter(Site.owner == userEmail).all()


@session_handler
def get_site_owner(siteID: str, session: Session = None) -> str:
    return session.query(Site).filter(Site.id == siteID).first().owner


@session_handler
def get_site_slug(siteID: str, session: Session = None) -> str:
    return session.query(Site).filter(Site.id == siteID).first().slug


@session_handler
def get_files(siteID: str, session: Session = None) -> List[PublishFile]:
    return session.query(PublishFile).filter(PublishFile.slug == siteID).all()
