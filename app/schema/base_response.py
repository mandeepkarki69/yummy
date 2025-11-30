# app/schema/base_response.py
from typing import Generic, Optional, List, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")

# Success response
class BaseResponse(GenericModel, Generic[T]):
    status: str = "success"
    message: str
    data: Optional[T] = None

# Error response
class ErrorDetail(BaseModel):
    field: Optional[str]
    error: str

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    errors: List[ErrorDetail] = Field(default_factory=list)
