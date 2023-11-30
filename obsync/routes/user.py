import uuid
import time
from fastapi import HTTPException, status, APIRouter
from jose import jwt
from sqlalchemy.exc import IntegrityError

from obsync.schemas.user import *
from obsync.utils import get_jwt_email
from obsync.db import vault
from obsync.db.exceptions import *
from obsync.config import config
from obsync.logger import logger

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/signup")
async def signup(request: SignUpRequest):
    """
    Allows a new user to sign up with their email, password, and optionally a signup key.

    The endpoint expects a JSON request with the following parameters:
    - **email**: The email address of the new user.
    - **password**: The password for the new user account.
    - **name**: The name of the new user.
    - **signup_key** (optional): A special key required for signup, if enabled in the system's configuration.

    Returns:
    - A confirmation with the user's email and name if the signup is successful.
    - `400 Bad Request` if the provided signup key is invalid.
    - `500 Internal Server Error` if there's any other error, such as if the user already exists.
    """
    if request.signup_key != config.SignUpKey and config.SignUpKey != "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signup key"
        )

    try:
        vault.new_user(request.email, request.password, request.name)
        logger.info(f"Created new user: {request.email}-{request.name}")
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) + "user exists")
    return {"email": request.email, "name": request.name}


@user_router.post("/signin")
async def signin(request: SigninRequest):
    """
    Authenticates a user and issues a JWT token based on their email and password.

    The endpoint expects a JSON request with the following parameters:
    - **email**: The user's email address.
    - **password**: The user's password.

    Returns:
    - A `SigninResponse` with the user's email, license, name, and a JWT token if authentication is successful.
    - Appropriate HTTP error response with details in case of a failed authentication attempt or other errors.
    """
    try:
        user_info = vault.login(request.email, request.password)
    except SigninException as e:
        raise HTTPException(status_code=e.retcode, detail=e.message)

    # Create JWT token
    try:
        token = jwt.encode({"email": user_info.email}, config.Secret, algorithm="HS256")
        logger.info(f"User {user_info.email} signed in")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return SigninResponse(
        email=user_info.email,
        license=user_info.license,
        name=user_info.name,
        token=token,
    )


@user_router.post("/info")
async def user_info(request: UserInfoRequest):
    """
    Retrieves information about the user identified by the provided JWT token.

    The endpoint expects a JSON request with the following parameter:
    - **token**: A JWT token for user authentication.

    Returns:
    - A `UserInfoResponse` containing user details if the token is valid and the user is found.
    - `401 Unauthorized` if the token is invalid or not provided.
    - `404 Not Found` if the user is not found.
    """
    email = get_jwt_email(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in"
        )

    user_info = vault.user_info(email)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserInfoResponse(
        uid=str(uuid.uuid4()),
        email=email,
        name=user_info.name,
        payment="",
        license="",
        credit=0,
        mfa=False,
        discount={
            "status": "approved",
            "expiry_ts": time.time() * 1000 + 365 * 24 * 60 * 60 * 1000,
            "type": "education",
        },
    )


@user_router.post("/signout", status_code=200)
async def signout():
    """
    Signs out the user. Currently, this endpoint does not perform any action but returns an empty response.

    Returns:
    - An empty response with a 200 OK status.
    """

    return {}


@user_router.post("/delete")
async def delete_user(request: UserInfoRequest):
    """
    Deletes a user identified by the provided JWT token.

    The endpoint expects a JSON request with the following parameter:
    - **token**: A JWT token for user authentication.

    Returns:
    - An empty response upon successful deletion.
    - `401 Unauthorized` if the token is invalid or not provided.
    """
    email = get_jwt_email(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in"
        )

    vault.delete_user(email)
    return {}
