"""All user crud operation"""

from fastapi import HTTPException
from firebase_admin import auth
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.sql_alchemy_models import User

from app.schemas._error import ErrorType, raise_app_error
from app.schemas._user import UserDataClient
from utils.firebase_admin_config import get_firebase_app

def create_user_data(db_user: User, db: Session) -> UserDataClient:
    """_summary_

    Args:
        db_user (User): User orm model db
        db (Session): database dependency

    Returns:
        UserDataClient: User data that client will receive
    """
    try:
        db.add(db_user)
        db.commit()
        firebase_app = get_firebase_app()
        #db.refresh(db_todo)
        print(db_user)
        auth.set_custom_user_claims(
            uid=str(db_user.user_id),
            custom_claims={'isRegistered': True},
            app=firebase_app
        )
        
        print(db_user)
        
        return UserDataClient(
            user_name = db_user.user_name
            
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise_app_error(
            error_code="DatabaseUserError",
            message="Failed to create new user record into the database.",
            error_type=ErrorType.DATA,
            status_code=500,
            details=str(e),
            additional_data={
                "operation": "insert",
                "model": "User"
            }
        )   

        
def update_user_data(
        user_id: str,
        user_email: str,
        update_data: UserDataClient,
        db: Session
    ) -> UserDataClient:
    """Update USER

    Args:
        user_id (str): user_id db
        update_data (UserDataClient): user data to update
        db (Session): dabase dependency

    Returns:
        UserDataClient: user data info limited with this model
    """
    try:
        db_user = db.query(User).filter(User.user_id==user_id).first()
        if db_user is None:
            raise HTTPException(
                    status_code=404,
                    detail='User not found'
                )
        # for key, value in update_data.model_dump(exclude_unset=True):
        #     setattr(db_user, key, value)

        db_user.user_name = update_data.user_name
        db_user.email = user_email

        db.commit()

        return UserDataClient(
            user_name = db_user.user_name,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise_app_error(
            error_code="DatabaseUserError",
            message="Failed to update User into the database.",
            error_type=ErrorType.DATA,
            status_code=500,
            details=str(e),
            additional_data={
                "operation": "update",
                "model": "User"
            }
        )



def get_user_data(user_id: str, db: Session) -> User:
    """
    Get a single USER item from the database.

    Args:
        user_id (str): The ID of the user item to retrieve.
        db (Session): The database session.

    Returns:
        UserDataClient: The retrieved User item filtered to send client
    """
    try:
        db_user = db.query(User).filter(User.user_id==user_id).first()
        if db_user is None:
            raise HTTPException(
                    status_code=404,
                    detail='User not found'
                )
        return  db_user
    except SQLAlchemyError as e:
        raise_app_error(
            error_code="DatabaseUserError",
            message="Failed to get User from the database.",
            error_type=ErrorType.DATA,
            status_code=500,
            details=str(e),
            additional_data={
                "operation": "get",
                "model": "User"
            }
        )
