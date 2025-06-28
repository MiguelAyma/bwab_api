
from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status, Header, Query
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.schemas._error import ErrorType, raise_app_error

from app.data._db_config import get_db

from app.service._raodmap_stage_crud import create_roadmap_stage_service
from utils._user_validation import get_current_user
from app.schemas._roadmap_stage import RoadmapStageResponse, RoadmapStageBase





router = APIRouter()

@router.post("/", response_model=RoadmapStageResponse)
async def insert_roadmap_stage(
    roadmap_stage: RoadmapStageBase,
    user_id="mX7QnagfucOIGRCshipiJUWhHzV2",
    db: Session = Depends(get_db),
    #ser_id: str = Depends(get_current_user), 
) -> RoadmapStageResponse:

    try :
        return create_roadmap_stage_service(
            roadmap_stage_create = roadmap_stage,
            db = db
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise_app_error(
            error_code="CreateRoadmapStageFailed",
            message="An unexpected error occurred while creating the roadmap stage.",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )