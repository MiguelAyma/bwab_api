from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data._db_config import get_db
from app.schemas._error import ErrorType, raise_app_error
from app.schemas._theme import ThemeBase, ThemeComplete, ThemeCreate, ThemeUpdate, ThemeResponse
from app.service._theme_crud import create_theme_service, get_complete_theme_by_id, get_theme_service, get_themes_per_user_service
from utils._user_validation import get_current_user



router = APIRouter()


@router.post("/", response_model=ThemeResponse)
async def insert_theme(
    theme: ThemeBase,
    #user_id="mX7QnagfucOIGRCshipiJUWhHzV2",
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ThemeResponse:
    try:
        return create_theme_service(theme_create=theme, db=db, user_id=user_id)
    except Exception as ex:
        raise_app_error(
            error_code="CreateThemeFailed",
            message="An unexpected error occurred while creating the theme.",
            error_type=ErrorType.HANDLER, 
            details=str(ex)
        )



@router.get("/{theme_id}", response_model=ThemeResponse)
async def get_theme_by_id(
    theme_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
) -> ThemeResponse:
    try:
        return get_theme_service(theme_id=theme_id, db=db)
    except Exception as ex:
        raise_app_error(
            error_code="GetThemeFailed",
            message="An unexpected error occurred while fetching the theme.",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )


@router.get("/{theme_id}/stages", response_model=ThemeComplete)
def get_theme_with_stages(
    theme_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    try:
        return get_complete_theme_by_id(theme_id, db)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise_app_error(
            error_code="RoadmapStageServiceError",
            message="Failed to fetch theme with stages.",
            error_type=ErrorType.SERVICE,
            details=str(ex)
        )
        
        
@router.get("/all-themes/", response_model=List[ThemeResponse])        
def get_all_themes_per_user(
    #user_id="mX7QnagfucOIGRCshipiJUWhHzV2",
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
) -> List[ThemeResponse]:

    try:
        return get_themes_per_user_service(
            user_id=user_id,
            db=db
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        raise_app_error(
            error_code="getThemesFailed",
            message="An unexpected error occurred while get the Themes.",
            error_type=ErrorType.HANDLER,
            details=str(ex)
        )
