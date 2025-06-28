import os
import firebase_admin
from firebase_admin import credentials, auth

try:
    
    current_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_path)

    path_credentials = os.path.join(project_root, 'credenciales_firebase.json')


    # Cargando las credenciales
    cred = credentials.Certificate(path_credentials)

    # Inicializando la aplicación de Firebase
    firebase_app = firebase_admin.initialize_app(cred)
    
    print("Credenciales validadas correctamente.")
    
except FileNotFoundError:
    print("Archivo de credenciales no encontrado.")
except ValueError as e:
    print(f"Error de valor: {e} - Revisa si la configuración de credenciales es correcta y el archivo existe.")
except firebase_admin.exceptions.FirebaseError as e:
    print(f"Error de Firebase: {e} - Posiblemente las credenciales no son válidas.")
except Exception as e:
    print(f"Error desconocido: {e}")

def get_firebase_app():
    #print(auth.get_user_by_email('claudio.ayma@outlook.com', app=firebase_app))
    return firebase_app
