from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    full_name: str
    profile_pic: Optional[str] = None
    bio: Optional[str] = None
    language: str = Field(default="en")
    theme: str = Field(default="light")

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_online: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    posts: List["Post"] = Relationship(back_populates="author")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_online: bool

# Friendships
class Friendship(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    friend_id: int = Field(foreign_key="user.id")
    status: str = Field(default="pending") # pending, accepted, blocked
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Social Media Content
class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    
    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    reactions: List["Reaction"] = Relationship(back_populates="post")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

    post: Post = Relationship(back_populates="comments")

class Reaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(default="like") # like, love, haha, etc.
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

    post: Post = Relationship(back_populates="reactions")
