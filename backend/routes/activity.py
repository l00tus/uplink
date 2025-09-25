from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..schemas.activity import ActivityCreate, ActivityRead, ActivityUpdate, ActivityDelete, ActivityJoinResponse, ActivitySimilarity
from ..services.activity import ActivityService
from ..services.auth import AuthService

router = APIRouter(prefix="/activities", tags=["activities"])

security = HTTPBearer()

@router.post("", response_model=ActivityRead)
async def create_activity(activity_data: ActivityCreate, token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> ActivityRead:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.create_activity(db, activity_data, current_user.id)

@router.get("", response_model=list[ActivityRead])
async def get_activities(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)) -> list[ActivityRead]:
    return await ActivityService.get_activities(db, skip=skip, limit=limit)

@router.get("/{activity_id}", response_model=ActivityRead)
async def get_activity_by_id(activity_id: int, db: AsyncSession = Depends(get_db)) -> ActivityRead:
    return await ActivityService.get_activity_by_id(db, activity_id)

@router.put("/{activity.id}", response_model=ActivityRead)
async def update_activity_by_id(activity_id: int, activity_data: ActivityUpdate, token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> ActivityRead:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.update_activity_by_id(db, activity_id, activity_data, current_user.id)

@router.delete("/{activity_id}", response_model=ActivityDelete)
async def delete_activity_by_id(activity_id: int, token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> ActivityDelete:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.delete_activity_by_id(db, activity_id, current_user.id)

@router.get("/me/hosted", response_model=list[ActivityRead])
async def get_my_hosted_activities(token: HTTPAuthorizationCredentials = Depends(security), skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)) -> list[ActivityRead]:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.get_activities_by_host(db, current_user.id, skip=skip, limit=limit)

@router.get("/me/joined", response_model=list[ActivityRead])
async def get_my_joined_activities(token: HTTPAuthorizationCredentials = Depends(security), skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)) -> list[ActivityRead]:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.get_activities_joined_by_user(db, current_user.id, skip=skip, limit=limit)

@router.post("/{activity_id}/join", response_model=ActivityJoinResponse)
async def join_activity(activity_id: int, token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> ActivityJoinResponse:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.join_activity(db, activity_id, current_user.id)

@router.delete("/{activity_id}/leave", response_model=ActivityJoinResponse)
async def leave_activity(activity_id: int, token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> ActivityJoinResponse:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.leave_activity(db, activity_id, current_user.id)

@router.get("/me/recommend", response_model=list[ActivitySimilarity])
async def recommend_activities(limit: int = 5, token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> list[ActivitySimilarity]:
    current_user = await AuthService.get_current_user(db, token.credentials)
    return await ActivityService.recommend_activities(db, current_user.id, limit=limit)