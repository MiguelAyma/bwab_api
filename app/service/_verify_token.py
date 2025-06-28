""" Service for firebase access token
"""

import os
from fastapi import HTTPException
import firebase_admin
from firebase_admin import credentials, auth
from app.schemas._user import FirebaseUserDecodedToken
from utils.firebase_admin_config import get_firebase_app


#current_path = os.path.dirname(os.path.abspath(__file__))
#project_root = os.path.dirname(current_path)

#path_credentials = os.path.join(project_root, 'credenciales_firebase.json')

# Inicializa la aplicación de Firebase con las credenciales del archivo JSON
#cred = credentials.Certificate(path_credentials)
#firebase_admin.initialize_app(cred)

def verify_access_token(access_token: str) -> FirebaseUserDecodedToken:
    """Verify a firebase access token 
    "RgFUwKFjzwSSlFR9cH5hBX72I9X2"
    Args:
        access_token (str): Firebase access token

    Returns:
        VerifyTokenOutput: _description_
    """
    #print(f"Token recibido: {access_token}")
    try:
        firebase_app = get_firebase_app()
        # firebase_admin.auth.set_custom_user_claims("RgFUwKFjzwSSlFR9cH5hBX72I9X2", {'isRegistered': True})
        # Verifica el ID Token con Firebase
        print('Hola')
        data = auth.verify_id_token(id_token=access_token, app=firebase_app)
        print('data')
        print(data)
        email_verified = data.get('email_verified')
        email = data.get('email')
        user_id = data.get('user_id')

        # Devuelve los valores obtenidos
        return FirebaseUserDecodedToken(
                    user_id=user_id,
                    email=email,
                    email_verified=email_verified,
                    valid_token=True
                )

    except Exception as e:
        raise Exception
        raise HTTPException(
                    status_code=500,
                    detail='Internal error verify_access_token'
                ) from e
