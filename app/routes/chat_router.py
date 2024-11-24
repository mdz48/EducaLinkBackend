from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.User import User
from app.models.chat import Chat
from app.schemas.chat_schema import ChatCreate, ChatResponse
from app.schemas.user_schema import UserResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

chatRoutes = APIRouter()

# Crear un nuevo chat
@chatRoutes.post('/chat/{receiver_id}', status_code=status.HTTP_201_CREATED, response_model=ChatResponse, tags=["Chats"])
async def create_chat(receiver_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    if receiver_id == current_user.id_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes iniciar un chat contigo mismo")
    if db.query(Chat).filter(Chat.sender_id == current_user.id_user, Chat.receiver_id == receiver_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este chat ya existe")
    # Comprobar si ya existe un chat con este usuario pero con las ids invertidas
    if db.query(Chat).filter(Chat.sender_id == receiver_id, Chat.receiver_id == current_user.id_user).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este chat ya existe")
    sender = db.query(User).filter(User.id_user == current_user.id_user).first()
    receiver = db.query(User).filter(User.id_user == receiver_id).first()
    db_chat = Chat(sender_id=current_user.id_user, receiver_id=receiver_id)
    db.add(db_chat)
    db.commit()
    
    return ChatResponse(id_chat=db_chat.id_chat, sender=UserResponse.from_orm(sender), receiver=UserResponse.from_orm(receiver))

# Obtener todos los chats
@chatRoutes.get('/chat/', response_model=List[ChatResponse], tags=["Chats"])
async def get_all_chats(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    chats = db.query(Chat).filter(Chat.sender_id == current_user.id_user).all()
    result = []
    for chat in chats:
        sender = db.query(User).filter(User.id_user == chat.sender_id).first()
        receiver = db.query(User).filter(User.id_user == chat.receiver_id).first()
        chat_response = ChatResponse(id_chat=chat.id_chat, sender=sender, receiver=receiver)
        result.append(chat_response)
    return result

# Obtener un chat por ID
@chatRoutes.get('/chat/{id_chat}', response_model=ChatResponse, tags=["Chats"])
async def get_chat_by_id(id_chat: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id_chat == id_chat, Chat.sender_id == current_user.id_user).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    sender = db.query(User).filter(User.id_user == chat.sender_id).first()
    receiver = db.query(User).filter(User.id_user == chat.receiver_id).first()
    chat_response = ChatResponse(id_chat=chat.id_chat, sender=sender, receiver=receiver)
    return chat_response

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
    result = []
    for chat in chats:
        sender = db.query(User).filter(User.id_user == chat.sender_id).first()
        receiver = db.query(User).filter(User.id_user == chat.receiver_id).first()
        chat_response = ChatResponse(id_chat=chat.id_chat, sender=sender, receiver=receiver)
        result.append(chat_response)
    return result