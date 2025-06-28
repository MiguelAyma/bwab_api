from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

from app.schemas._user import FirebaseUserDecodedToken

from app.service._verify_token import verify_access_token
from utils._helpers import get_current_user_dep




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth/token", auto_error=False)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)



async def get_current_user(
    access_token: Optional[str] = Depends(api_key_header),
    oauth2_token: Optional[str] = Depends(oauth2_scheme)
):
    print('############ get_current_user called!')
    if access_token:
        print('access_token')
        try:
            token_decode: FirebaseUserDecodedToken = verify_access_token(access_token)
            if token_decode.valid_token:
                return token_decode.user_id
        except Exception:
            pass  # Puedes registrar el error si lo deseas

    if oauth2_token:
        print('oauth_token')
        try:
            user_id = await get_current_user_dep(oauth2_token)
            return user_id
        except Exception:
            pass  # Puedes registrar el error si lo deseas

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
    )
