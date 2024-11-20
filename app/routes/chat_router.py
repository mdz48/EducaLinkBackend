from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.chat import Chat
from app.schemas.chat_schema import ChatCreate, ChatResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

chatRoutes = APIRouter()

# Crear un nuevo chat
@chatRoutes.post('/chat/', status_code=status.HTTP_201_CREATED, response_model=ChatResponse, tags=["Chats"])
async def create_chat(chat: ChatCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    if chat.receiver_id == current_user.id_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes iniciar un chat contigo mismo")
    if db.query(Chat).filter(Chat.sender_id == current_user.id_user, Chat.receiver_id == chat.receiver_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este chat ya existe")
    db_chat = Chat(**chat.model_dump(exclude={'sender_id'}), sender_id=current_user.id_user)
    db.add(db_chat)
    db.commit()
    return db_chat

# Obtener todos los chats
@chatRoutes.get('/chat/', response_model=List[ChatResponse], tags=["Chats"])
async def get_all_chats(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    chats = db.query(Chat).filter(Chat.sender_id == current_user.id_user).all()
    return chats

# Obtener un chat por ID
@chatRoutes.get('/chat/{id_chat}', response_model=ChatResponse, tags=["Chats"])
async def get_chat_by_id(id_chat: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id_chat == id_chat, Chat.sender_id == current_user.id_user).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat

# Actualizar un chat por ID
@chatRoutes.put('/chat/{id_chat}', response_model=ChatResponse, tags=["Chats"])
async def update_chat(id_chat: int, chat: ChatCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_chat = db.query(Chat).filter(Chat.id_chat == id_chat, Chat.sender_id == current_user.id_user).first()
    if not db_chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    db_chat.update(**chat.model_dump())
    db.commit()
    return db_chat

# Eliminar un chat por ID
@chatRoutes.delete('/chat/{id_chat}', status_code=status.HTTP_204_NO_CONTENT, tags=["Chats"])
async def delete_chat(id_chat: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_chat = db.query(Chat).filter(Chat.id_chat == id_chat, Chat.sender_id == current_user.id_user).first()
    if not db_chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    db.delete(db_chat)
    db.commit()
    
# Obtener todos los chats de un usuario donde esta involucrado
@chatRoutes.get('/chat/user/{id_user}', response_model=List[ChatResponse], tags=["Chats"])
async def get_chats_by_user(id_user: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    chats = db.query(Chat).filter(
        (Chat.sender_id == id_user) | (Chat.receiver_id == id_user)
    ).all()
    return chats