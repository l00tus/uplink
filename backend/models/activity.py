from ..core.database import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import BIGINT, JSONB, TIMESTAMP
from pgvector.sqlalchemy import Vector

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(BIGINT, primary_key=True, index=True)
    host_id = Column(BIGINT, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False, server_default=text("''::text"))
    tags = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    location = Column(String, nullable=False)
    date_time = Column(TIMESTAMP(timezone=True), nullable=False)
    max_participants = Column(Integer, nullable=False)
    participants = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))    
    status = Column(String, nullable=False, server_default=text("'active'"))
    embedding = Column(Vector(384), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
