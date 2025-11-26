from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.controller import user_controller
from app.controller import auth_controller
from app.core.database import engine, Base
import asyncio

from app.core.exception_handlers import http_exception_handler, validation_exception_handler

app = FastAPI(title="Yummy API", version="1.0")


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include routers
app.include_router(user_controller.router)
app.include_router(auth_controller.router)

# Create tables at startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
