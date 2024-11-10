from fastapi import FastAPI, Depends,status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pymongo.mongo_client import MongoClient
from app.shared.config.mongoConnection import client
from app.shared.config.db import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user_router import userRoutes
from app.routes.employeeRouter import employeeRoutes
from app.routes.forum_router import forumRoutes
from app.routes.post_router import postRoutes
from app.routes.comment_router import commentRoutes
from app.routes.sale_post_router import salePostRoutes
from app.routes.chat_router import chatRoutes
from app.routes.message_router import messageRoutes
app = FastAPI()

app.include_router(userRoutes)
# app.include_router(employeeRoutes)
app.include_router(forumRoutes)
app.include_router(postRoutes)
app.include_router(commentRoutes)
app.include_router(salePostRoutes)
app.include_router(chatRoutes)
app.include_router(messageRoutes)
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

