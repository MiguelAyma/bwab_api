""" Service USER crud operation """

from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

#from app.data._sqlalchemy_models import User,Account,Credit
from app.models.sql_alchemy_models import User


from app.data._user_crud import create_user_data, get_user_data, update_user_data
from app.schemas._error import ErrorType, raise_app_error
from app.schemas._user import UserCreateBase, UserCreateResponse, UserDataClient, UserDataResponse
from app.schemas._user import FirebaseUserDecodedToken

from firebase_admin import credentials, auth 


def create_user_service(
    user_create: UserDataClient,
    user_id: str,
    user_email: str,
    db: Session
) -> UserDataClient:
    """User create service

    Args:
        user_create (UserDataClient): User data that comes from client.
        user_id (str): Firebase user ID.
        user_email (str): User's email address.
        db (Session): Database session.

    Returns:
        UserDataClient: User data to respond to the client.
    """
    try:
        # Crear el usuario
        db_user = User(
            user_id=user_id,
            user_name=user_create.user_name,
            email=user_email
        )
        # Crear el usuario en la base de datos
        create_user_data(db_user, db)

        return UserDataClient(
            user_name=db_user.user_name
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise_app_error(
            error_code="UserServiceError",
            message="Failed to create User in service layer.",
            error_type=ErrorType.SERVICE,
            details=str(e)
        )

def update_user_service(
        user_update: UserDataClient,
        user_id: str,
        user_email: str,
        db:Session
    ) -> UserDataClient:
    """User create service

    Args:
        user_create (UserDataClient): User data that come from client
        user_id (str): user_id
        user_email (str): user_email
        db (Session): db dependency

    Raises:
        HTTPException: error handling create_user_service

    Returns:
        UserDataClient: User data to response to client
    """
    try:
        return update_user_data(
            db=db,
            update_data=user_update,
            user_id=user_id,
            user_email=user_email
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise_app_error(
            error_code="UserServiceError",
            message="Failed to update User in service layer.",
            error_type=ErrorType.SERVICE,
            details=str(e)
        )


def get_user_by_id_service(
        #token_decode: FirebaseUserDecodedToken,
        user_id: str,
        db: Session
    ) -> UserDataResponse:
    """Obtain user by id service

    Args:
        token_decode (FirebaseUserDecodedToken): Decoded token to get the userid and validate
        db (Session): db dependency

    Raises:
        HTTPException: _description_

    Returns:
        UserDataClient: _description_
    """
    try:
        user = get_user_data(user_id=user_id, db=db)
        return UserDataResponse(
            user_name= user.user_name,
            email= user.email,
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise_app_error(
            error_code="UserServiceError",
            message="Failed to get User in service layer.",
            error_type=ErrorType.SERVICE,
            details=str(e)
        )





