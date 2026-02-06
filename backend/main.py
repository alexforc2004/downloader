from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select
from datetime import timedelta
from models import User, UserRead, Friendship, Post, Comment, Reaction
from schemas import PostCreate, PostRead, CommentCreate, CommentRead, ReactionCreate, ReactionRead
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from database import engine, get_db
from typing import List
import os
from downloader import downloader

# Social Network API & alexDownloader
# To start the Telegram Bot, run: .\venv\Scripts\python.exe telegram_bot.py
# To start the API, run: .\venv\Scripts\uvicorn.exe main:app --port 8000

app = FastAPI(title="Social Network API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Database Setup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/register", response_model=UserRead)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.exec(select(User).where(User.username == user_data.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        profile_pic=user_data.profile_pic,
        bio=user_data.bio,
        language=user_data.language,
        theme=user_data.theme
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Friend Requests
@app.post("/friends/request/{friend_id}")
async def send_friend_request(friend_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself")
    
    existing = db.exec(select(Friendship).where(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id))
    )).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Friendship or request already exists")
    
    friendship = Friendship(user_id=current_user.id, friend_id=friend_id, status="pending")
    db.add(friendship)
    db.commit()
    return {"message": "Friend request sent"}

@app.get("/friends/requests", response_model=List[UserRead])
async def get_friend_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friendships = db.exec(select(Friendship).where(Friendship.friend_id == current_user.id, Friendship.status == "pending")).all()
    user_ids = [f.user_id for f in friendships]
    users = db.exec(select(User).where(User.id.in_(user_ids))).all()
    return users

@app.post("/friends/accept/{sender_id}")
async def accept_friend_request(sender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friendship = db.exec(select(Friendship).where(
        Friendship.user_id == sender_id, 
        Friendship.friend_id == current_user.id, 
        Friendship.status == "pending"
    )).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Request not found")
    
    friendship.status = "accepted"
    db.add(friendship)
    db.commit()
    return {"message": "Friend request accepted"}

# Posts
@app.post("/posts", response_model=PostRead)
async def create_post(post_data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = Post(content=post_data.content, image_url=post_data.image_url, user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@app.get("/posts", response_model=List[PostRead])
async def get_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # In a real app, we would only get friends' posts. For now, get all.
    return db.exec(select(Post).order_by(Post.created_at.desc())).all()

# Comments
@app.post("/comments", response_model=CommentRead)
async def create_comment(comment_data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = Comment(content=comment_data.content, post_id=comment_data.post_id, user_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

# Reactions
@app.post("/reactions", response_model=ReactionRead)
async def react_to_post(reaction_data: ReactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if existing reaction
    existing = db.exec(select(Reaction).where(Reaction.post_id == reaction_data.post_id, Reaction.user_id == current_user.id)).first()
    if existing:
        existing.type = reaction_data.type
        db.add(existing)
    else:
        existing = Reaction(type=reaction_data.type, post_id=reaction_data.post_id, user_id=current_user.id)
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket, db: Session):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        # Update online status
        user = db.get(User, user_id)
        if user:
            user.is_online = True
            db.add(user)
            db.commit()

    def disconnect(self, user_id: int, db: Session):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # Update offline status
        user = db.get(User, user_id)
        if user:
            user.is_online = False
            db.add(user)
            db.commit()

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    db_gen = get_db()
    db = next(db_gen)
    await manager.connect(user_id, websocket, db)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle messages
    except WebSocketDisconnect:
        manager.disconnect(user_id, db)
    finally:
        db.close()

# Media Downloader Endpoints
def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.get("/downloader/info")
async def get_media_info(url: str):
    try:
        return downloader.get_info(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/downloader/download")
async def download_media(url: str, format_type: str = "video", background_tasks: BackgroundTasks = None):
    try:
        data = downloader.download_media(url, format_type)
        file_path = data["path"]
        title = data["title"]
        
        if background_tasks:
            background_tasks.add_task(remove_file, file_path)
        
        ext = "mp3" if format_type == "audio" else "mp4"
        filename = f"{title}.{ext}"
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
