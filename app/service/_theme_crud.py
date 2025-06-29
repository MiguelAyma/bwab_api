from typing import List
from fastapi import HTTPException
from pyparsing import Optional
from sqlalchemy.orm import Session

from app.schemas._error import ErrorType, raise_app_error
from app.schemas._roadmap_stage import RoadmapStageResponse
from app.schemas._theme import ThemeBase, ThemeComplete, ThemeCreate, ThemeUpdate, ThemeResponse, ThemeNotFoundError
from app.models.sql_alchemy_models import Theme
from app.data._theme_crud import create_theme_data, get_theme_by_id_data, get_themes_per_user_data

def generate_default_content(title: str, description: str) -> str:
    return f"Contenido generado automáticamente para el tema   Contenidos: contenido4, contenido5, contenido6, contenido7, contenido8, contenido9, contenido10 '{title}'. Descripción: {description}."


def create_theme_service(theme_create: ThemeBase, db: Session, user_id: str) -> ThemeResponse:
    try:
         # Determinar el contenido
        content_value = theme_create.content

        if not theme_create.keep_content or content_value is None:
            # Si keep_content es False o no hay content, generamos uno nuevo
            content_value = generate_default_content(theme_create.title, theme_create.description)
            
        db_theme = Theme(
            user_id=user_id,
            title=theme_create.title,
            content=content_value,
            progress=0,
            #num_stages=theme_create.num_stages,
            num_stages=5,
            description=theme_create.description,
            keep_content=theme_create.keep_content
        )
        record = create_theme_data(db_theme, db)
        return ThemeResponse(
            theme_id=record.theme_id,
            user_id=record.user_id,
            title=record.title,
            content=record.content,
            progress=record.progress,
            num_stages=record.num_stages,
            description=record.description,
            keep_content=record.keep_content,
            created_at=record.created_at,
            updated_at=record.updated_at
        )

    except Exception as e:
        raise_app_error(
            error_code=ErrorType.SERVICE,
            message="Failed to create Theme in service layer.",
            error_type=ErrorType.SERVICE,
            details=str(e)
        )



def get_theme_service(theme_id: int, db: Session) -> ThemeResponse:
    try:
        theme = get_theme_by_id_data(theme_id, db)
        if not theme:
            raise ThemeNotFoundError()

        return ThemeResponse(
            theme_id=theme.theme_id,
            user_id=theme.user_id,
            title=theme.title,
            content=theme.content,
            progress=theme.progress,
            num_stages=theme.num_stages,
            created_at=theme.created_at,
            updated_at=theme.updated_at
        )
    except ThemeNotFoundError:
        raise_app_error(
            error_code="ThemeNotFound",
            message="Theme not found.",
            error_type="VALIDATION",
            status_code=404,
            details=f"theme_id: {theme_id}"
        )
    except Exception as e:
        raise_app_error(
            error_code="ThemeServiceError",
            message="Failed to get Theme in service layer.",
            error_type="SERVICE",
            details=str(e)
        )

def get_complete_theme_by_id(theme_id: int, db: Session) -> ThemeComplete:
    theme = get_theme_by_id_data(theme_id, db)

    if not theme:
        raise_app_error(
            error_code="ThemeNotFound",
            message=f"Theme with ID {theme_id} not found.",
            error_type=ErrorType.DATA,
        )
        
    return ThemeComplete(
        theme_data=ThemeResponse.model_validate(theme),
        roadmap_stages=[RoadmapStageResponse.model_validate(stage) for stage in theme.roadmap_stages]
    )

def get_themes_per_user_service(db: Session, user_id: str) -> List[ThemeResponse]:
    try:
        themes: List[Theme] = get_themes_per_user_data(user_id, db)
        
        if not themes:
            raise HTTPException(
                status_code=404,
                detail=f"No themes found for this user"
            )
        
        # Convertir todos los registros de SQLAlchemy a Pydantic
        return [
            ThemeResponse(
                theme_id=theme.theme_id,
                user_id=theme.user_id,
                title=theme.title,
                content=theme.content,
                progress=theme.progress,
                num_stages=theme.num_stages,
                created_at=theme.created_at,
                updated_at=theme.updated_at
            )
            for theme in themes
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        # Manejar otros errores inesperados
        raise_app_error(
            error_code="THEME_SERVICE_ERROR",
            message="Failed to retrieve themes in service layer.",
            error_type=ErrorType.SERVICE,
            details=str(e)
        )


