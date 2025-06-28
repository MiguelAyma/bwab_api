import logging
from firebase_admin.exceptions import FirebaseError
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status, Response, Path, Query
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.schemas._error import ErrorType, raise_app_error
from app.service._verify_token import verify_access_token
from app.data._db_config import get_db
from app.schemas._user import FirebaseUserDecodedToken,UserDataResponse,UserCreateBase, UserCreateResponse
from utils._user_validation import get_current_user


from app.service._user_crud import (
    create_user_service, 
    get_user_by_id_service,
    update_user_service, 

)    


from app.schemas._user import (
    UserDataClient, 
    FirebaseUserDecodedToken,
)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
router = APIRouter()

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new User",
    response_model=UserDataClient
    )
async def insert_user(
    user: UserDataClient,
    db: Session = Depends(get_db),
    access_token: str = Depends(api_key_header)
) -> UserDataClient:
    """Create a new user in the system.
    
    This endpoint validates the Firebase access token and creates a new user
    with the provided data if authentication is successful.

    Args:
        user (UserDataClient): User data received from client
        db (Session): Database session instance
        access_token (str): Firebase access token for authentication

    Returns:
        UserDataClient: Created user data

    Raises:
        HTTPException: 401 if token is invalid
        HTTPException: 403 if email is not verified
        HTTPException: 500 if database operation fails
    """
    try:
        token_decode: FirebaseUserDecodedToken = verify_access_token(access_token)
        
        if not token_decode.valid_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return create_user_service(
            user_create=user,
            user_id=token_decode.user_id,
            user_email=token_decode.email,
            db=db
        )
    except FirebaseError as fe:
        logger.error(f"Firebase authentication error: {str(fe)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise_app_error(
            error_code="CreateUserFailed",
            message="An unexpected error occurred while create User.",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )
        
@router.get(
    "/", 
    status_code=status.HTTP_200_OK,
    summary="Get User",
    response_model=UserDataResponse
)
async def get_user_by_id(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
) -> UserDataResponse:
    """
    Token URl For OAuth Code Grant Flow

    Args:
        grant_type (str): Grant Type
        code (Optional[str], optional)
        refresh_token (Optional[str], optional)
    Returns:
        mssg (str)
        status_code (int)
    """
    try :
        user= get_user_by_id_service(user_id, db)
        if user is not None:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise_app_error(
            error_code="GetUserFailed",
            message="An unexpected error occurred while getting User",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )
        
@router.put(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Update User",     
    response_model=UserDataClient
)
async def update_user(
    user: UserDataClient,
    db: Session = Depends(get_db),
    access_token: str = Depends(api_key_header)
) -> UserDataClient:
    """User insert operation

    Args:
        user (UserCreate): User data received from client.
        request (Request): Information from the request
        db (Session, optional): Database object. Defaults to Depends(get_db).
        access_token (str, optional): Access token that comes in headers
        this is an access token from firebase. Defaults to Depends(api_key_header).

    Returns:
        _type_: _description_
    """
    try :
        token_decode: FirebaseUserDecodedToken = verify_access_token(access_token)

        if token_decode.valid_token is True: #and token_decode.email_verified is True:
            return update_user_service(
                        user_update=user,
                        user_id=token_decode.user_id,
                        user_email=token_decode.email,
                        db=db
                    )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise_app_error(
            error_code="UpdateUserFailed",
            message="An unexpected error occurred while update User.",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )
        

        
        