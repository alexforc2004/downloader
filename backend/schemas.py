from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    content: str
    image_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    created_at: datetime
    user_id: int

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int

class CommentRead(CommentBase):
    id: int
    created_at: datetime
    user_id: int
    post_id: int

class ReactionBase(BaseModel):
    type: str = "like"

class ReactionCreate(ReactionBase):
    post_id: int

class ReactionRead(ReactionBase):
    id: int
    user_id: int
    post_id: int
