from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal




class EvaluationBase(BaseModel):
    theme_id: str# = Field(..., max_length=300)
    title: Optional[str] #= Field(None, max_length=2000)
    description: Decimal #= Field(..., ge=0, le=100)
    order_index: Optional[int] = None
    flashcards:Optional[dict] = None
    concept_map: Optional[dict] = None
    icon: Optional[str] =None #Field(None, max_length=30)  # campo para emoji
    progress: Decimal 

class EvaluationResponse(EvaluationBase):
    roadmap_stage_id: int
    created_at: datetime
    updated_at: datetime


#json_campo:list[Optional[str]]