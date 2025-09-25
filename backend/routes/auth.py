from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..schemas.user import UserCreate, UserRead
from ..schemas.auth import UserLogin, Token
from ..services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

# Checks for token
security = HTTPBearer() 

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> Token:
    return await AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    return await AuthService.login_user(db, credentials)

@router.get("/me", response_model=UserRead)
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> UserRead:
    return await AuthService.get_current_user(db, token.credentials)

@router.post("/refresh", response_model=Token)
async def refresh_token(token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> Token:
    return await AuthService.refresh_token(db, token.credentials)