from decimal import Decimal
from typing import List
from fastapi import HTTPException

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.sql_alchemy_models import Evaluation

from app.schemas._error import ErrorType, raise_app_error #, CategoryNotFoundError, DeleteCategoryResponse

def get_evaluation_by_id_data(evaluation_id: int, db: Session) -> Evaluation | None:
    """Obtiene un registro de evaluación específico por su ID (el intento del usuario)."""
    return db.query(Evaluation).filter(Evaluation.evaluation_id == evaluation_id).first()

def get_evaluation_template_data(theme_id: int, db: Session) -> Evaluation | None:
    """
    Obtiene la plantilla de evaluación para un tema, buscando la que no tiene respuestas.
    """

    return db.query(Evaluation).filter(
        Evaluation.theme_id == theme_id,
        Evaluation.answers == None
    ).first()

def update_evaluation_score_data(
    evaluation_to_update: Evaluation,
    score: float,
    user_answers_as_dict: list,
    db: Session
) -> Evaluation:
    """
    Actualiza una evaluación existente con el puntaje y las respuestas del usuario.
    """
    evaluation_to_update.score = score
    # --- CORRECCIÓN ---
    # Guardamos las respuestas en la columna 'answers'.
    evaluation_to_update.answers = { user_answers_as_dict}
  
    
    db.commit()
    db.refresh(evaluation_to_update)
    return evaluation_to_update