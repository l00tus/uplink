from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..schemas.user import UserCreate, UserRead, UserUpdate, UserDelete
import bcrypt

class UserService:
    async def create_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
        existing_user_query = select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
        result = await db.execute(existing_user_query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
                
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            interests=user_data.interests,
            bio=user_data.bio,
            country=user_data.country,
            city=user_data.city,
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return new_user
    
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return db_user
    
    async def get_user_by_username(db: AsyncSession, username: str) -> UserRead:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return db_user
    
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[UserRead]:
        if limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit cannot exceed 100"
            )
            
        query = select(User).offset(skip).limit(limit)
        result = await db.execute(query)
        db_users = result.scalars().all()
        
        return db_users
    
    async def update_user_by_id(db: AsyncSession, user_id: int, user_data: UserUpdate) -> UserRead:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Check for username conflicts
        if 'username' in update_data:
            username_query = select(User).where(
                User.username == update_data['username'],
                User.id != user_id
            )
            result = await db.execute(username_query)
            existing_username = result.scalar_one_or_none
            
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    
    async def delete_user_by_id(db: AsyncSession, user_id: int) -> UserDelete:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await db.delete(db_user)
        await db.commit()
        
        return UserDelete(message=f"User {user_id} deleted successfully")