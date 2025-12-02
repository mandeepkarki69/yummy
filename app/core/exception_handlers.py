# app/core/exception_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from app.schema.base_response import ErrorResponse, ErrorDetail

# Handle HTTPException
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail if isinstance(exc.detail, str) else "An error occurred",
            "errors": []
        }
    )

# Handle validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    def _field(loc):
        last = loc[-1] if loc else "unknown"
        return str(last)

    errors = [ErrorDetail(field=_field(e["loc"]), error=e["msg"]) for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation failed",
            "errors": [e.dict() for e in errors]
        }
    )
