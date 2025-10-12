from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.embedding_model import get_embeddings
from ..models.activity import Activity
from ..models.user import User
from ..schemas.activity import ActivityCreate, ActivityRead, ActivityUpdate, ActivityDelete, ActivityJoinResponse, ActivitySimilarity
import numpy as np

class ActivityService:
    async def create_activity(db: AsyncSession, activity_data: ActivityCreate, host_id: int) -> ActivityRead:
        activity_embedding = get_embeddings(activity_data.tags)
        
        new_activity = Activity(
            host_id=host_id,
            title=activity_data.title,
            description=activity_data.description,
            tags=activity_data.tags,
            location=activity_data.location,
            date_time=activity_data.date_time,
            max_participants=activity_data.max_participants,
            participants=[],
            status="active",
            embedding=activity_embedding
        )
        
        db.add(new_activity)
        await db.commit()
        await db.refresh(new_activity)
        
        return new_activity
    
    async def get_activities(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[ActivityRead]:
        if limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit cannot exceed 50"
            )
        
        query = select(Activity).offset(skip).limit(limit)
        result = await db.execute(query)
        activities = result.scalars().all()
        
        return activities
    
    async def get_activity_by_id(db: AsyncSession, activity_id: int) -> ActivityRead:
        query = select(Activity).where(Activity.id == activity_id)
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        return activity

    async def update_activity_by_id(db: AsyncSession, activity_id: int, activity_data: ActivityUpdate, user_id: int) -> ActivityRead:
        query = select(Activity).where(Activity.id == activity_id)
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        # Check if user is the host
        if activity.host_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the host can update this activity"
            )
        
        update_data = activity_data.model_dump(exclude_unset=True)
        
        if 'max_participants' in update_data:
            new_max = update_data['max_participants']
            current_count = len(activity.participants)
            if new_max < current_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot reduce max participants to {new_max}. Activity already has {current_count} participants."
                )

        for field, value in update_data.items():
            setattr(activity, field, value)
        
        if 'tags' in update_data:
            activity.embedding = get_embeddings(update_data['tags'])
        
        await db.commit()
        await db.refresh(activity)
        
        return activity
    
    async def delete_activity_by_id(db: AsyncSession, activity_id: int, user_id: int) -> ActivityDelete:
        query = select(Activity).where(Activity.id == activity_id)
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        if activity.host_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the host can delete this activity"
            )
        
        await db.delete(activity)
        await db.commit()
        
        return ActivityDelete(message=f"Activity '{activity.title}' deleted successfully")
    
    async def get_activities_by_host(db: AsyncSession, host_id: int, skip: int = 0, limit: int = 50) -> list[ActivityRead]:
        query = select(Activity).where(Activity.host_id == host_id)
        query = query.order_by(Activity.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        return activities
    
    async def get_activities_joined_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50) -> list[ActivityRead]:
        query = select(Activity).where(Activity.participants.op('@>')([user_id]))
        query = query.order_by(Activity.date_time.asc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        return activities
    
    async def join_activity(db: AsyncSession, activity_id: int, user_id: int) -> ActivityJoinResponse:
        query = select(Activity).where(Activity.id == activity_id)
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        # Check if activity is active
        if activity.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot join inactive activity"
            )
        
        # Check if user is the host
        if activity.host_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Host cannot join their own activity"
            )
        
        # Check if user already joined
        if user_id in activity.participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already joined this activity"
            )
        
        # Check if activity is full
        if len(activity.participants) >= activity.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Activity is full ({len(activity.participants)}/{activity.max_participants})"
            )
        
        activity.participants = activity.participants + [user_id]
        
        await db.commit()
        await db.refresh(activity)
        
        return ActivityJoinResponse(message="Successfully joined activity")
    
    async def leave_activity(db: AsyncSession, activity_id: int, user_id: int) -> ActivityJoinResponse:
        query = select(Activity).where(Activity.id == activity_id)
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        if user_id not in activity.participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not a participant in this activity"
            )
        
        # Remove user from participants
        activity.participants = [pid for pid in activity.participants if pid != user_id]
        
        await db.commit()
        await db.refresh(activity)
        
        return ActivityJoinResponse(message="Successfully left activity")
    
    async def recommend_activities(db: AsyncSession, user_id: int, limit: int) -> list[ActivitySimilarity]:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    
        result = await db.execute(select(Activity).where(Activity.status == "active"))
        activities = result.scalars().all()
        
        scores = []
        
        for activity in activities:
            score = ActivityService.cosine_similarity(user.embedding, activity.embedding)
            scores.append((activity, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top = scores[:limit]
        
        return [
            ActivitySimilarity(
                activity_id=activity.id,
                title=activity.title,
                description=activity.description,
                date_time=activity.date_time,
                location=activity.location,
                max_participants=activity.max_participants,
                tags=activity.tags,
                similarity=similarity
            )
            for activity, similarity in top
        ]
        
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0
        
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        
