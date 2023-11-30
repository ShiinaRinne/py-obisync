from pydantic import BaseModel
from typing import Optional


class SigninRequest(BaseModel):
    email: str
    password: str


class SigninResponse(BaseModel):
    email: str
    license: str
    name: str
    token: str


class UserInfoRequest(BaseModel):
    token: str


class UserInfoResponse(BaseModel):
    uid: str
    email: str
    name: str
    payment: str
    license: str
    credit: int
    mfa: bool
    discount: dict


class SignUpRequest(BaseModel):
    email: str
    password: str
    name: str
    signup_key: Optional[str] = None
