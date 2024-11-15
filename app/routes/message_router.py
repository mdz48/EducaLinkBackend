from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.User import User
from app.models.message import Message
from app.schemas.message_schema import MessageCreate, MessageResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

messageRoutes = APIRouter()

# Crear un nuevo mensaje
@messageRoutes.post('/message/', status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def create_message(message: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(current_user.id_user or "No user")
    if message.sender_id == current_user.id_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't send a message to yourself")
    db_message = Message(**message.model_dump(exclude={'date_message'}), date_message=datetime.now(), sender_id=current_user.id_user)
    db.add(db_message)
    db.commit()
    return db_message

# Obtener todos los mensajes de un chat
@messageRoutes.get('/message/chat/{chat_id}', response_model=List[MessageResponse])
async def get_messages_by_chat(chat_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    return messages

# Obtener un mensaje por ID
@messageRoutes.get('/message/{id_message}', response_model=MessageResponse)
async def get_message_by_id(id_message: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    message = db.query(Message).filter(Message.id_message == id_message, Message.user_id == current_user.id_user).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return message

# Actualizar un mensaje por ID
@messageRoutes.put('/message/{id_message}', response_model=MessageResponse)
async def update_message(id_message: int, message: MessageCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_message = db.query(Message).filter(Message.id_message == id_message, Message.sender_id == current_user.id_user).first()
    if not db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    # Asignar los nuevos valores directamente
    for key, value in message.model_dump(exclude={'date_message', 'sender_id'}).items():
        setattr(db_message, key, value)
    
    db_message.date_message = datetime.now()
    db_message.sender_id = current_user.id_user
    
    db.commit()
    db.refresh(db_message)  # Refrescar el objeto para obtener los valores actualizados
    return db_message

# Eliminar un mensaje por ID
@messageRoutes.delete('/message/{id_message}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(id_message: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_message = db.query(Message).filter(Message.id_message == id_message).first()
    if not db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    db.delete(db_message)
    db.commit()
    
    
