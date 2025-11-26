from fastapi import FastAPI

from app.controller import user_controller
from app.controller import auth_controller
from app.core.database import engine, Base
import asyncio

app = FastAPI(title="Yummy API", version="1.0")

# Include routers
app.include_router(user_controller.router)
app.include_router(auth_controller.router)

# Create tables at startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
