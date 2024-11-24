from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.User import User
from app.models.chat import Chat
from app.models.message import Message
from app.models.sale_message import SaleMessage
from app.models.sale_schat import SaleChat
from app.schemas.message_schema import MessageCreate, MessageResponse, SaleMessageResponse
from app.schemas.user_schema import UserResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

messageRoutes = APIRouter()

# Crear un nuevo mensaje
@messageRoutes.post('/message/{chat_id}', status_code=status.HTTP_201_CREATED, response_model=MessageResponse, tags=["Mensajes"])
async def create_message(chat_id: int, message: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(current_user.id_user or "No user")
    # Verificar si el chat existe
    if not db.query(Chat).filter(Chat.id_chat == chat_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat no existe")
    sender = db.query(User).filter(User.id_user == current_user.id_user).first()
    db_message = Message(message=message, chat_id=chat_id, sender_id=current_user.id_user, date_message=datetime.now())
    db.add(db_message)
    db.commit()
    return MessageResponse(id_message=db_message.id_message, message=db_message.message, chat_id=db_message.chat_id, sender=UserResponse.from_orm(sender), date_message=db_message.date_message)

# Obtener todos los mensajes de un chat
@messageRoutes.get('/message/chat/{chat_id}', response_model=List[MessageResponse], tags=["Mensajes"])
async def get_messages_by_chat(chat_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    result = [] 
    for message in messages:
        sender = db.query(User).filter(User.id_user == message.sender_id).first()
        result.append(MessageResponse(id_message=message.id_message, message=message.message, chat_id=message.chat_id, sender=UserResponse.from_orm(sender), date_message=message.date_message))
    return result

# Obtener un mensaje por ID
@messageRoutes.get('/message/{id_message}', response_model=MessageResponse, tags=["Mensajes"])
async def get_message_by_id(id_message: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Cambios realizados aquí
    message = db.query(Message).filter(Message.id_message == id_message, Message.sender_id == current_user.id_user).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    sender = db.query(User).filter(User.id_user == message.sender_id).first()
    return MessageResponse(id_message=message.id_message, message=message.message, chat_id=message.chat_id, sender=UserResponse.from_orm(sender), date_message=message.date_message)

# Actualizar un mensaje por ID
@messageRoutes.put('/message/{id_message}', response_model=MessageResponse, tags=["Mensajes"])
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
    sender = db.query(User).filter(User.id_user == db_message.sender_id).first()
    return MessageResponse(id_message=db_message.id_message, message=db_message.message, chat_id=db_message.chat_id, sender=UserResponse.from_orm(sender), date_message=db_message.date_message)

# Eliminar un mensaje por ID
@messageRoutes.delete('/message/{id_message}', status_code=status.HTTP_204_NO_CONTENT, tags=["Mensajes"])
async def delete_message(id_message: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_message = db.query(Message).filter(Message.id_message == id_message).first()
    if not db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    db.delete(db_message)
    db.commit()
    
# SECCIÓN DE MENSAJES DE VENTA
@messageRoutes.post('/sale_message/{sale_chat_id}', status_code=status.HTTP_201_CREATED, response_model=SaleMessageResponse, tags=["Sale Messages"])
async def create_sale_message(sale_chat_id: int, message: str, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # Verificar si el chat de venta existe
    if not db.query(SaleChat).filter(SaleChat.id_sale_chat == sale_chat_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sale chat not found")
    sender = db.query(User).filter(User.id_user == current_user.id_user).first()
    db_sale_message = SaleMessage(message=message, sale_chat_id=sale_chat_id, sender_id=current_user.id_user, date_message=datetime.now())
    db.add(db_sale_message)
    db.commit()
    return SaleMessageResponse(id_sale_message=db_sale_message.id_sale_message, message=db_sale_message.message, sale_chat_id=db_sale_message.sale_chat_id, sender=UserResponse.from_orm(sender), date_message=db_sale_message.date_message)

# Obtener todos los mensajes de un chat de venta
@messageRoutes.get('/sale_message/chat/{sale_chat_id}', response_model=List[SaleMessageResponse], tags=["Sale Messages"])
async def get_sale_messages_by_chat(sale_chat_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    messages = db.query(SaleMessage).filter(SaleMessage.sale_chat_id == sale_chat_id).all()
    result = []
    for message in messages:
        sender = db.query(User).filter(User.id_user == message.sender_id).first()
        result.append(SaleMessageResponse(id_sale_message=message.id_sale_message, message=message.message, sale_chat_id=message.sale_chat_id, sender=UserResponse.from_orm(sender), date_message=message.date_message))
    return result

# Obtener un mensaje de venta por ID
@messageRoutes.get('/sale_message/{id_sale_message}', response_model=SaleMessageResponse, tags=["Sale Messages"])
async def get_sale_message_by_id(id_sale_message: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    message = db.query(SaleMessage).filter(SaleMessage.id_sale_message == id_sale_message, SaleMessage.sender_id == current_user.id_user).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale message not found")
    sender = db.query(User).filter(User.id_user == message.sender_id).first()
    return SaleMessageResponse(id_sale_message=message.id_sale_message, message=message.message, sale_chat_id=message.sale_chat_id, sender=UserResponse.from_orm(sender), date_message=message.date_message)


# Eliminar un mensaje de venta por ID
@messageRoutes.delete('/sale_message/{id_sale_message}', status_code=status.HTTP_204_NO_CONTENT, tags=["Sale Messages"])
async def delete_sale_message(id_sale_message: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_sale_message = db.query(SaleMessage).filter(SaleMessage.id_sale_message == id_sale_message, SaleMessage.sender_id == current_user.id_user).first()
    if not db_sale_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale message not found")
    db.delete(db_sale_message)
    db.commit()
    
# FIN SECCIÓN DE MENSAJES DE VENTA