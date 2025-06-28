""" All pydantic models related to USERS
"""
import datetime
from pydantic import BaseModel, Field
from typing import List
#from app.data._sqlalchemy_models import GenderEnum

from typing import Dict, Any, Optional

class UserDataClient(BaseModel):
    """User information model before to insert into DB
    """
    user_name: str
    #email: str
 


class FirebaseUserDecodedToken(BaseModel):
    """Information that is stored in firebases user access token
    """
    user_id: str
    email: str
    email_verified: bool
    valid_token: bool

class UserDataResponse(UserDataClient):
    email: str
    
class UserCreateBase(BaseModel):
    user_name: str
    email: str
    password:Optional[str] = None
    
class UserCreateResponse(UserCreateBase):
    user_id: str
