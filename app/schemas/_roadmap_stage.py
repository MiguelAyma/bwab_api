from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from pydantic import Field
from typing import Dict, Any



class RoadmapStageBase(BaseModel):
    theme_id: int# = Field(..., max_length=300)
    title: Optional[str] #= Field(None, max_length=2000)
    description: str #= Field(..., ge=0, le=100)
    order_index: int
    flashcards:Dict[str, Any] 
    concept_map: Dict[str, Any]
    icon: str #Field(None, max_length=30)  # campo para emoji
    progress: float 

 
class RoadmapStageResponse(RoadmapStageBase):
    roadmap_stage_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


#jsonB_campo:list[Optional[str]]
