from ..core.database import Base
from sqlalchemy import Column, String, Text, func, text
from sqlalchemy.dialects.postgresql import BIGINT, JSONB, TIMESTAMP

class User(Base):
    __tablename__ = "users"
    
    id = Column(BIGINT, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    interests = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    bio = Column(Text, nullable=True, server_default=text("''::text"))
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())