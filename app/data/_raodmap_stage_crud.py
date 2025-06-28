from typing import List
from fastapi import HTTPException

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.sql_alchemy_models import RoadmapStage

from app.schemas._error import ErrorType, raise_app_error #, CategoryNotFoundError, DeleteCategoryResponse


def create_roadmap_stage_data(db_roadmap_stage: RoadmapStage, db: Session) -> RoadmapStage:
    """CREATE Roadmap Stage

    Args:
        db_roadmap_stage (RoadmapStage): RoadmapStage db model
        db (Session): database dependency

    Raises:
        HTTPException: If a sql operation present errors

    Returns:
        Category: Category db model with data after inserting
    """
    try:
        db.add(db_roadmap_stage)
        db.commit()
        # db.refresh(db_roadmap_stage)

        return db_roadmap_stage
    except SQLAlchemyError as e:
        db.rollback()
        raise_app_error(
            error_code="DatabaseRoadmapStageError",
            message="Failed to insert the new Roadmap Stage into the database.",
            error_type=ErrorType.DATA,
            status_code=500,
            details=str(e),
            additional_data={
                "operation": "insert",
                "model": "RoadmapStage"
            }
        )