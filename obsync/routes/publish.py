
import uuid
import time
from fastapi import HTTPException, status, APIRouter, Request
from urllib.parse import unquote
from jose import jwt
from sqlalchemy.exc import IntegrityError

from obsync.utils import get_jwt_email
from obsync.db import publish
from obsync.db.models.publish import *
from obsync.db.exceptions import *
from obsync.schemas.publish import *
from obsync.config import config
from obsync.logger import logger


publish_router = APIRouter(prefix="/publish", tags=["publish"])
api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.post("/list")
@publish_router.post("/list")
async def list_sites( request: ListSitesRequest):
    email = get_jwt_email(request.token)
    if request.id == "":
        sites = publish.get_sites(email)
        return {
            "sites": sites,
            "shared": [],
            "limit": config.MaxSitesPerUser,
        }
    siteOwner = publish.get_site_owner(request.id)
    files = publish.get_files(request.id)
    return {
        "files": files,
        "owner": siteOwner == email,
    }


@publish_router.post("/create")
async def create_site( request: CreateSiteRequest):
    email = get_jwt_email(request.token)
    sites = publish.get_sites(email)
    if len(sites) >= config.MaxSitesPerUser:
        raise HTTPException(status_code=status.HTTP_200_OK, detail=f"You have reached the limit of {config.MaxSitesPerUser} site")
    site = publish.create_site(email)
    return site


@publish_router.post("/delete")
async def delete_site( request: DeleteSiteRequest):
    email = get_jwt_email(request.token)
    siteOwner = publish.get_site_owner(request.site_uid)
    if email != siteOwner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this site")
    publish.delete_site(request.site_uid)
    return {}


@api_router.post("/slugs")
async def get_slug_info( request: GetSlugInfoRequest):
    email = get_jwt_email(request.token)
    
    if len(request.ids) == 0: return {}
    
    siteSlugs = {}
    for id in request.ids:
        slug = publish.get_site_slug(id)
        siteSlugs[id] = slug
        
    return siteSlugs


@api_router.post("/site")
async def site_info(request: SiteInfoRequest):
    email = get_jwt_email(request.token)
    site = publish.get_slug(request.slug)
    if site is None:
        return {
            "code": "NOTFOUND",
            "message": "Slug not found",
        }
    
    return site


@api_router.post("/remove")
async def remove_file(request: RemoveFileRequest):
    email = get_jwt_email(request.token)
    siteOwner = publish.get_site_owner(request.id)
    if siteOwner != email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this file")
    publish.remove_file(request.id, request.path)
    return {}


@api_router.post("/upload")
async def upload_file(request: Request):
    token = request.headers.get("obs-token")
    email= get_jwt_email(token)

    content_length = request.headers.get("content-length")
    obs_hash = request.headers.get("obs-hash")
    obs_id = request.headers.get("obs-id")
    obs_path = request.headers.get("obs-path")

    try:
        obs_path = unquote(obs_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    site_owner= publish.get_site_owner(obs_id)
    if site_owner != email:
        raise HTTPException(status_code=403, detail="You do not have permission to upload to this site")

    try:
        data = await request.body()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    file = PublishFile(
        size=content_length,
        hash=obs_hash,
        slug=obs_id,
        path=obs_path,
        data=data.decode('utf-8')
    )

    try:
        publish.new_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {}


@api_router.post("/slug")
async def configure_site_slug(request: ConfigureSiteSlugRequest):
    email = get_jwt_email(request.token)
    siteOwner = publish.get_site_owner(request.id)
    if email != siteOwner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to change this site's slug")
    publish.set_slug(request.slug, request.id)
    return {}


@publish_router.get("/{slug}")
async def get_site_index(slug: str):
    site = publish.get_slug(slug)
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    files = publish.get_files(site.id)
    if files is None:
        raise HTTPException(status_code=500, detail="Error retrieving files")
    return files
    
    
@publish_router.get("/{slug}/{path:path}")
async def get_published_file(slug: str, path: str):
    if path is None or path == '':
        return await get_site_index(slug)
    
    site = publish.get_slug(slug)
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    file = publish.get_file(site.id, path)
    if file is None:
        raise HTTPException(status_code=500, detail="File not found or error retrieving file")
    
    return file


    