from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_services import AuthServices
from app.schema.user_schema import Token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/",)
def test():
    return {"hello": "world"}

@router.post("/login", response_model=Token)
async def login(credentials: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    
    service = AuthServices(db)
    return await service.login(credentials)
