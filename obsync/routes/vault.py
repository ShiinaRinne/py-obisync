from fastapi import Body, HTTPException, status, APIRouter
from typing import List, Dict
from obsync.schemas.vault import *
from obsync.utils import get_jwt_email, generate_password
from obsync.db import vault as crud_vault
from obsync.logger import logger

vault_router = APIRouter(prefix="/vault", tags=["vault"])


@vault_router.post("/create")
async def create_vault(request: CreateVaultRequest = Body(...)) -> VaultInfo:
    """
    Creates a new vault with the provided name, salt, and keyhash, authenticated by the user's token.


    The endpoint expects a JSON request with the following parameters:
    - **token**: A JWT token for user authentication.
    - **name**: Name of the new vault.
    - **salt** (optional): Salt for the vault's password. If not provided, a random one is generated.
    - **keyhash** (optional): Keyhash for added security. Must be provided if salt is provided.

    Returns:
    - The newly created vault's information.
    - `400 Bad Request` if keyhash is required but not provided.
    - `401 Unauthorized` if the token is invalid.
    - `500 Internal Server Error` for any other server errors.
    """
    email = get_jwt_email(request.token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    password = ""
    salt = ""
    keyhash = ""

    if request.salt is None or request.salt == "":
        password = generate_password(20, 5, 5, False, True)
        salt = generate_password(20, 5, 5, False, True)
        keyhash = ""
    else:
        salt = request.salt
        if request.keyhash is None or request.keyhash == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="keyhash must be provided if salt is provided",
            )
        else:
            keyhash = request.keyhash

    try:
        vault = crud_vault.new_vault(request.name, email, password, salt, keyhash)
        logger.info(f"Created new vault: {vault.id}-{vault.name}")
        return vault
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@vault_router.post("/list")
async def list_vaults(
    request: ListVaultRequest = Body(...),
) -> Dict[str, List[VaultInfo]]:
    """
    Lists all vaults associated with a user's email, derived from the provided token.

    The endpoint expects a JSON request with the following parameter:
    - **token**: A JWT token for user authentication.

    Returns:
    - A dictionary of user's own vaults and shared vaults.
    - `401 Unauthorized` if the token is invalid.
    - `500 Internal Server Error` for any other server errors.
    """
    email = get_jwt_email(request.token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    try:
        vaults: List[VaultInfo] = crud_vault.get_vaults(email)
        shared_vaults: List[VaultInfo] = crud_vault.get_shared_vaults(email)
        return {"shared": shared_vaults, "vaults": vaults}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@vault_router.post("/access")
async def access_vault(request: AccessVaultRequest = Body(...)):
    """
    Allows access to a specific vault using a provided token, vault UID, and key hash.

    The endpoint expects a JSON request with the following parameters:
    - **token**: A JWT token for user authentication.
    - **vault_uid**: Unique identifier of the vault to be accessed.
    - **keyhash**: A hash key for additional security.

    Returns:
    - A success response containing user details and access confirmation if the user is authorized and the vault exists.
    - `401 Unauthorized` if the token is invalid or the user doesn't have access to the specified vault.
    - `404 Not Found` if the vault or user is not found.
    - `500 Internal Server Error` for any other server errors.
    """
    email = get_jwt_email(request.token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    if not crud_vault.has_access_to_vault(request.vault_uid, email):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have access to this vault",
        )

    try:
        vault_data = crud_vault.get_vault(request.vault_uid, request.keyhash)
        if vault_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vault not found"
            )

        user = crud_vault.user_info(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {
            "allowed": True,
            "email": email,
            "name": user.name,
            "useruid": "b094fc51bf40b9ddb9ff43d4aadfa962",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@vault_router.post("/delete")
async def delete_vault(request: DeleteVaultRequest = Body(...)) -> Dict:
    """
    Deletes a Vault based on the provided token and vault_uid.

    This endpoint expects a JSON formatted request body containing the following parameters:
    - **token**: A JWT token used for authentication.
    - **vault_uid**: The unique identifier of the Vault to be deleted.

    If the operation is successful, it returns a dictionary containing status information.
    Different status codes are returned in the following scenarios:
    - `401 Unauthorized`: If the provided token is invalid.
    - `500 Internal Server Error`: If any internal server error occurs during the deletion process.

    Returns:
        Dict: Returns `{"status": "ok"}` if the operation is successful.
    """
    email = get_jwt_email(request.token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    try:
        crud_vault.delete_vault(request.vault_uid, email)
        logger.info(f"Deleted vault: {request.vault_uid}")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
