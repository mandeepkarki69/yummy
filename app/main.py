import logging
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.controller import user_controller
from app.controller import auth_controller
from app.controller import restaurant_controller
from app.controller import restaurant_table_type_controller
from app.controller import restaurant_table_controller
from app.controller import item_category_controller
from app.controller import menu_controller
from app.controller import order_controller

from app.core.database import engine, Base
from app.core.config import settings
from app.utils.role_checker import RoleChecker
import asyncio

from app.core.exception_handlers import http_exception_handler, validation_exception_handler

app = FastAPI(title="Yummy API", version="1.0")

BASE_DIR = Path(__file__).resolve().parents[0]
UPLOAD_ROOT = BASE_DIR / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_ROOT), name="uploads")

logger = logging.getLogger("yummy.middleware")

# Simple in-memory counters for basic monitoring
REQUEST_COUNT = 0


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-ms"] = f"{duration_ms:.2f}"
    logger.info("%s %s -> %s in %.2fms", request.method, request.url.path, response.status_code, duration_ms)
    return response


RATE_LIMIT_STATE: dict[str, dict[str, float | int]] = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Very simple per-IP fixed-window rate limiting
    limit = settings.RATE_LIMIT_REQUESTS
    window = settings.RATE_LIMIT_WINDOW_SECONDS

    if limit > 0 and window > 0:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        entry = RATE_LIMIT_STATE.get(client_ip)

        if entry is None or now - entry["window_start"] > window:
            RATE_LIMIT_STATE[client_ip] = {"window_start": now, "count": 1}
        else:
            if entry["count"] >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests, please try again later",
                )
            entry["count"] += 1

    response = await call_next(request)
    return response


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include routers
app.include_router(user_controller.router)
app.include_router(auth_controller.router)
app.include_router(restaurant_controller.router)
app.include_router(restaurant_table_controller.router)
app.include_router(restaurant_table_type_controller.router)
app.include_router(item_category_controller.router)
app.include_router(menu_controller.router)
app.include_router(order_controller.router)


@app.get("/health", tags=["Monitoring"])
async def health():
    return {"status": "ok"}


@app.get(
	"/metrics/basic",
	tags=["Monitoring"],
	dependencies=[Depends(RoleChecker(["superadmin"]))],
)
async def basic_metrics():
    return {"total_requests": REQUEST_COUNT}

# Create tables at startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
