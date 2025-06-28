from enum import Enum
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    SERVICE = "ServiceError"
    DATA = "DataError"
    HANDLER = "HandlerError"
    VALIDATION = "ValidationError"
    AUTHENTICATION = "AuthenticationError"
    AUTHORIZATION = "AuthorizationError"

class AppError(BaseModel):
    error: str  # Short error code, ex: "CreateTransactionFailed"
    message: str  # Human-readable message
    type: ErrorType
    details: Optional[str] = None  # Optional stack trace or technical info
    additional_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    
def raise_app_error(
    *,
    error_code: str,
    message: str,
    error_type: ErrorType,
    details: Optional[str] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    additional_data: Optional[Dict[str, Any]] = None
):
    app_error = AppError(
        error=error_code,
        message=message,
        type=error_type,
        details=details,
        additional_data=additional_data or {}
    )
    raise HTTPException(status_code=status_code, detail=app_error.model_dump())