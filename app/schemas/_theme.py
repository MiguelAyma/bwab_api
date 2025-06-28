from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.schemas._roadmap_stage import RoadmapStageResponse    



class ThemeBaseV0(BaseModel):
    title: str = Field(..., max_length=300)
    content: Optional[str] =None #Field(None, max_length=2000)
    progress: Decimal = Field(..., ge=0, le=100)
    num_stages: Optional[int] = None

class ThemeBase(BaseModel):
    title: str = Field(..., max_length=300)
    description: str
    content: Optional[str] =None #Field(None, max_length=2000)
    keep_content: bool 
    progress: Decimal =None
    num_stages: Optional[int] = None 
    
class ThemeResponse(ThemeBase):
    theme_id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
    


class ThemeComplete(BaseModel):
    theme_data: ThemeResponse
    roadmap_stages: list[RoadmapStageResponse]
    model_config = ConfigDict(from_attributes=True)




class ThemeCreate(ThemeBase):
    user_id: str


class ThemeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    content: Optional[str] = Field(None, max_length=2000)
    progress: Optional[Decimal] = Field(None, ge=0, le=100)
    num_stages: Optional[int] = None





class ThemeNotFoundError(Exception):
    """Exception raised when a Theme item is not found in the database."""
    pass

