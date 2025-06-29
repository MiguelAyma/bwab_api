
from pyparsing import Optional
from sqlalchemy.orm import Session

from app.schemas._error import ErrorType, raise_app_error
from app.schemas._evaluation import EvaluationBase, EvaluationInput, EvaluationOutput, EvaluationResponse, Question
from fastapi import HTTPException
from app.models.sql_alchemy_models import Evaluation
from app.data._evaluation_crud import  get_evaluation_by_id_data, get_evaluation_template_data, update_evaluation_score_data
from decimal import Decimal, ROUND_HALF_UP
def get_evaluation_service(evaluation_id: int, db: Session) ->EvaluationOutput:
    try:
        evaluation = get_evaluation_by_id_data(evaluation_id, db)
        if not evaluation:
            raise HTTPException(status_code=404, detail="evaluation not found")

        return EvaluationOutput(
            evaluation_id=evaluation.evaluation_id,
            theme_id=evaluation.theme_id,
            roadmap_stage_id=evaluation.roadmap_stage_id,
            questions=evaluation.questions,
        )

    except Exception as e:
        raise_app_error(
            error_code="EvaluationServiceError",
            message="Failed to get Evaluation in service layer.",
            error_type=ErrorType.SERVICE,
            details=str(e)
        )
        
def complete_evaluation_service(
    submission: EvaluationInput,
    db: Session
) -> EvaluationResponse:
    """
    Califica una evaluación, la actualiza en la BD y devuelve un EvaluationResponse.
    """
    evaluation_id = submission.evaluation_id
    user_answers = submission.answers or []

    # 1. Obtener el intento de evaluación del usuario que se va a actualizar
    user_attempt = get_evaluation_by_id_data(evaluation_id, db)
    if not user_attempt:
        raise HTTPException(status_code=404, detail=f"Evaluation attempt with id {evaluation_id} not found.")

    # 2. Obtener la plantilla para saber las respuestas correctas
    template = get_evaluation_template_data(user_attempt.theme_id, db)
    if not template or not template.questions:
        raise HTTPException(status_code=404, detail=f"Evaluation template for theme id {user_attempt.theme_id} not found.")

    # 3. Lógica para CALIFICAR la evaluación
    questions_data = template.questions.get('questions', [])
    correct_answers_map = {q['question_num']: q['index_correct'] for q in questions_data}
    
    total_questions = len(correct_answers_map)
    if total_questions == 0:

        score = Decimal("0.00")
    else:
        correct_count = 0
        for answer in user_answers:
            if correct_answers_map.get(answer.question_num) == answer.index_selected:
                correct_count += 1
        
        score_val = (Decimal(correct_count) / Decimal(total_questions)) * 100
        score = score_val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


    user_answers_dict = [answer.model_dump() for answer in user_answers]
    updated_db_eval = update_evaluation_score_data(
        evaluation_to_update=user_attempt,
        score=score,
        user_answers_as_dict=user_answers_dict,
        db=db
    )


    questions_for_response = [Question(**q) for q in questions_data]

    return EvaluationResponse(
        evaluation_id=updated_db_eval.evaluation_id,
        theme_id=updated_db_eval.theme_id,
        roadmap_stage_id=updated_db_eval.roadmap_stage_id,
        questions=questions_for_response,
        answers=user_answers,
        score=updated_db_eval.score,
        created_at=updated_db_eval.created_at,
        updated_at=updated_db_eval.updated_at
    )
