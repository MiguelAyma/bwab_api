from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import OperationalError

import time
import os
from dotenv import load_dotenv, find_dotenv



_: bool = load_dotenv(find_dotenv())



DB_URL = os.getenv("DB_URL")


if DB_URL is None:
    raise Exception("No DB_URL environment variable found")

# Enable connection pooling with pessimistic testing
engine = create_engine(DB_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency with retry mechanism for OperationalError
def get_db():
    attempt_count = 0
    max_attempts = 5
    retry_delay = 2  # seconds

    while attempt_count < max_attempts:
        try:
            db = SessionLocal()
            yield db  # Solo entra aquí si la conexión fue exitosa
            return     # Salir correctamente tras yield
        except OperationalError as e:
            print(f"SSL connection error occurred: {e}, retrying...")
            attempt_count += 1
            time.sleep(retry_delay)
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise e
        finally:
            try:
                db.close()
            except:
                pass  # Ignorar errores al cerrar

    raise RuntimeError("Failed to connect to the database after several attempts.")

