from ast import Delete
from pydantic import BaseModel
from typing import Optional

from obsync.db.db import Base

class ListSitesRequest(BaseModel):
    token: str
    version: Optional[int] = 0
    id: Optional[str] = ""
    

class CreateSiteRequest(BaseModel):
    token: str
    
    
class DeleteSiteRequest(BaseModel):
    token: str
    site_uid: str
  

class ConfigureSiteSlugRequest(BaseModel):
    token: str
    id: Optional[str] = ""
    slug: str
    

class GetSlugInfoRequest(BaseModel):
    token: str
    ids: list
    
    
class SiteInfoRequest(BaseModel):
    token: str
    slug: str
    
    
class RemoveFileRequest(BaseModel):
    token: str
    site_uid: str
    path: str
    
    
class UploadFileRequest(BaseModel):
    # should get from header
    pass


class GetPublishedFile(BaseModel):
    # should get from url
    pass
    