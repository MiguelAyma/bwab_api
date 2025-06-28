from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

#from app.data._sqlalchemy_models import Category
from app.models.sql_alchemy_models import RoadmapStage 
from app.data._raodmap_stage_crud import    create_roadmap_stage_data
from app.schemas._roadmap_stage import RoadmapStageResponse,RoadmapStageBase
from app.schemas._error import ErrorType, raise_app_error

def create_roadmap_stage_service(
    roadmap_stage_create: RoadmapStageBase,
    db: Session
) -> RoadmapStageResponse:
    try:
        db_roadmap_stage = RoadmapStage(
            theme_id=roadmap_stage_create.theme_id,
            title=roadmap_stage_create.title,
            description=roadmap_stage_create.description,
            order_index=roadmap_stage_create.order_index,
            flashcards=roadmap_stage_create.flashcards,
            concept_map=roadmap_stage_create.concept_map,
            icon=roadmap_stage_create.icon,
            progress=roadmap_stage_create.progress
        )
        record: RoadmapStage = create_roadmap_stage_data(db_roadmap_stage, db)

        return RoadmapStageResponse(
            roadmap_stage_id=record.roadmap_stage_id,
            theme_id=record.theme_id,
            title=record.title,
            description=record.description,
            order_index=record.order_index,
            flashcards=record.flashcards,
            concept_map=record.concept_map,
            progress=record.progress,
            
            icon=record.icon,
            created_at=record.created_at,
            updated_at=record.updated_at
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise_app_error(
            error_code="RoadmapStageServiceError",
            message="Failed to create RoadmapStage in service layer.",
            error_type=ErrorType.SERVICE,
            details=str(e)
        )