from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal







#json_campo:list[Optional[str]]





class QuestionOutput(BaseModel):
    """
    Representa una única pregunta que se envía al cliente.
    No contiene la respuesta correcta por seguridad.
    """
    id: int          # ID único y estable de la pregunta (de tu base de datos).
    question: str    # El texto de la pregunta.
    options: list[str] # La lista de posibles opciones.

class EvaluationOutput(BaseModel):
    """
    Representa la evaluación completa que se envía al cliente para que la resuelva.
    """
    evaluation_id: int # Un ID único para este intento de evaluación específico.
    theme_id: int
    roadmap_stage_id: Optional[int] = None
    questions: list[QuestionOutput]



# --- Modelos para recibir datos del Frontend ---

class UserAnswerInput(BaseModel):
    """
    Representa la respuesta de un usuario a una ÚNICA pregunta.
    Es ligero y preciso.
    """
    question_id: int   # El ID de la pregunta que se está respondiendo.
    selected_option_index: int # El índice de la opción que el usuario seleccionó.

class EvaluationSubmissionInput(BaseModel):
    """
    Representa el envío completo de la evaluación por parte del usuario.
    """
    evaluation_id: int       # El ID del intento de evaluación para vincularlo.
    answers: list[UserAnswerInput] # La lista de respuestas del usuario.
    
    
    
class Option(BaseModel):
    id:int
    text: str
class Question(BaseModel):
    question_num:int
    question: str
    options: list[Option]
    index_correct: int

class Answer(BaseModel):
    question_num: int
    index_selected: int


class EvaluationOutput(BaseModel):
    evaluation_id:int
    theme_id:int
    roadmap_stage_id:Optional[int] = None
    questions:list[Question] 

    
class EvaluationInput(BaseModel):
    evaluation_id:int
    answers:Optional[list[Answer]]
    
    
    
    
class EvaluationBase(BaseModel):
    theme_id:int
    roadmap_stage_id:Optional[int] = None
    questions:list[Question] 
    answers:Optional[list[Answer]] = None
    score: Optional[Decimal] = None
    
class EvaluationResponse(EvaluationBase):
    evaluation_id:int
    created_at: datetime
    updated_at: datetime