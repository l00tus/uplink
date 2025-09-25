from pydantic import BaseModel, Field
from datetime import datetime

class ActivityBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(default="", max_length=1000)
    tags: list[str]
    location: str
    date_time: datetime
    max_participants: int = Field(gt=0, le=100)

class ActivityCreate(ActivityBase):
    pass

class ActivityRead(ActivityBase):
    id: int
    host_id: int
    participants: list[int]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None
    location: str | None = None
    date_time: datetime | None = None
    max_participants: int | None = Field(default=None, gt=0, le=100)

class ActivityDelete(BaseModel):
    message: str
    
class ActivityJoinResponse(BaseModel):
    message: str
    
class ActivitySimilarity(BaseModel):
    activity_id: int
    title: str
    description: str
    date_time: datetime
    location: str
    max_participants: int
    similarity: float