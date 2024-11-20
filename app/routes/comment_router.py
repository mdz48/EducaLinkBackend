from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.comment import Comment
from app.schemas.comment_schema import CommentCreate, CommentResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

commentRoutes = APIRouter()

# Crear un nuevo comentario
@commentRoutes.post('/comment/', status_code=status.HTTP_201_CREATED, response_model=CommentResponse, tags=["Comentarios"])
async def create_comment(comment: CommentCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_comment = Comment(
        **comment.model_dump(exclude={'comment_date'}),
        comment_date=datetime.now(),
        user_id=current_user.id_user
    )
    db.add(db_comment)
    db.commit()
    return db_comment

# Obtener todos los comentarios
@commentRoutes.get('/comment/', response_model=List[CommentResponse], tags=["Comentarios"])
async def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments

# Obtener un comentario por ID
@commentRoutes.get('/comment/{id_comment}', response_model=CommentResponse, tags=["Comentarios"])
async def get_comment_by_id(id_comment: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id_comment == id_comment).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

# Actualizar un comentario
@commentRoutes.put('/comment/{id_comment}', response_model=CommentResponse, tags=["Comentarios"])
async def update_comment(id_comment: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_comment = db.query(Comment).filter(Comment.id_comment == id_comment).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    db_comment.comment_text = comment.comment_text
    db.commit()
    return db_comment

# Eliminar un comentario
@commentRoutes.delete('/comment/{id_comment}', status_code=status.HTTP_204_NO_CONTENT, tags=["Comentarios"])
async def delete_comment(id_comment: int, db: Session = Depends(get_db)):
    db_comment = db.query(Comment).filter(Comment.id_comment == id_comment).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    db.delete(db_comment)
    db.commit()
    
# Obtener comentarios por ID de post
@commentRoutes.get('/comments/post/{post_id}', response_model=List[CommentResponse], tags=["Comentarios"])
async def get_comments_by_post_id(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments
