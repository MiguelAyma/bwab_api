from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data._db_config import get_db
from app.schemas._error import ErrorType, raise_app_error
from app.schemas._evaluation import EvaluationResponse,EvaluationBase, EvaluationOutput, EvaluationInput
from app.service._evaluation_crud import complete_evaluation_service, get_evaluation_service
from utils._user_validation import get_current_user




router = APIRouter()


@router.get("/{evaluation_id}", response_model=EvaluationOutput)#EvaluationResponse)
async def get_evaluation_by_id(
    evaluation_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
) -> EvaluationOutput:
    try:
        return get_evaluation_service(evaluation_id=evaluation_id, db=db)
    except Exception as ex:
        raise_app_error(
            error_code="GetEvaluationFailed",
            message="An unexpected error occurred while fetching the evaluation.",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )
        

@router.put("/", response_model=EvaluationResponse)
async def complete_evaluation(
    submission: EvaluationInput, # El cuerpo de la petición es de tipo EvaluationInput
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Endpoint para enviar las respuestas de una evaluación.
    Recibe el ID de la evaluación y las respuestas en el cuerpo,
    la califica, guarda el resultado y devuelve la evaluación completa.
    """
    try:
        return complete_evaluation_service(submission=submission, db=db)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise_app_error(
            error_code="CompleteEvaluationFailed",
            message="An unexpected error occurred while completing the evaluation.",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )


