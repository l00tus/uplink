from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..schemas.user import UserCreate, UserRead, UserUpdate, UserDelete
from ..services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await UserService.create_user(db, user_data)

@router.get("", response_model=list[UserRead])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> list[UserRead]:
    return await UserService.get_users(db, skip=skip, limit=limit)

@router.get("/id/{user_id}", response_model=UserRead)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await UserService.get_user_by_id(db, user_id)

@router.get("/{username}", response_model=UserRead)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await UserService.get_user_by_username(db, username)

@router.put("/{user_id}", response_model=UserRead)
async def update_user_by_id(user_id: int, user_data:UserUpdate, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await UserService.update_user_by_id(db, user_id, user_data)

@router.delete("/{user_id}", response_model=UserDelete)
async def delete_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)) -> UserDelete:
    return await UserService.delete_user_by_id(db, user_id)