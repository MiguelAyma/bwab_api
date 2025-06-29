from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.sql_alchemy_models import Theme
from app.schemas._error import ErrorType, raise_app_error
from app.schemas._roadmap_stage import RoadmapStageResponse
from app.schemas._theme import ThemeComplete, ThemeResponse


def create_theme_data(db_theme: Theme, db: Session) -> Theme:
    try:
        db.add(db_theme)
        db.commit()
        db.refresh(db_theme)
        return db_theme
    except SQLAlchemyError as e:
        db.rollback()
        raise_app_error(
            error_code="DatabaseThemeError",
            message="Failed to insert the new Theme into the database.",
            error_type=ErrorType.DATA,
            status_code=500,
            details=str(e),
            additional_data={"operation": "insert", "model": "Theme"}
        )


def get_theme_by_id_data(theme_id: int, db: Session) -> Theme | None:
    return db.query(Theme).filter(Theme.theme_id == theme_id).first()



def get_themes_per_user_data(user_id:str ,db: Session) -> List[Theme]:

    try:
        db_themes = db.query(Theme).filter(           
            Theme.user_id == user_id
        ).all()
        if db_themes is None:
            raise HTTPException(
                    status_code=404,
                    detail='Themes not found'
                )
        return  db_themes
    except SQLAlchemyError as e:
        raise_app_error(
            error="DatabaseThemeError",
            message="Failed to get Theme from the database.",
            type=ErrorType.DATA,
            status_code=500,
            details=str(e),
            additional_data={
                "operation": "get_all_per_user",
                "model": "Theme"
            }
        )
