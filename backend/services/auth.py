
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from ..core.config import settings
from ..core.embedding_model import get_embeddings
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..schemas.auth import UserLogin, Token
import bcrypt
import jwt


class AuthService:
    SECRET_KEY = settings.JWT_SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    async def register_user(db: AsyncSession, user_data: UserCreate) -> Token:
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
        user_embedding = get_embeddings(user_data.interests)

        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            interests=user_data.interests,
            bio=user_data.bio,
            country=user_data.country,
            city=user_data.city,
            embedding=user_embedding
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        access_token_expires = timedelta(minutes=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(data={"sub": str(new_user.id)}, expires_delta=access_token_expires)
        
        return Token(access_token=access_token, token_type="bearer", expires_in=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    async def login_user(db: AsyncSession, credentials: UserLogin) -> Token:
        user = await AuthService.authenticate_user(db, credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token_expires = timedelta(minutes=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
        
        return Token(access_token=access_token, token_type="bearer", expires_in=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    async def get_current_user(db: AsyncSession, token: str) -> UserRead:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=[AuthService.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception
        
        query = select(User).where(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise credentials_exception
        
        return user
        
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, AuthService.SECRET_KEY, AuthService.ALGORITHM)
        
        return encoded_jwt
    
    async def refresh_token(db: AsyncSession, token: str) -> Token:
        # Get current user to validate the token
        current_user = await AuthService.get_current_user(db, token)
        
        access_token_expires = timedelta(minutes=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": str(current_user.id)}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> User | None:
        query = select(User).where(User.username == credentials.username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not AuthService.verify_password(credentials.password, user.hashed_password):
            return None
        
        return user
        
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))