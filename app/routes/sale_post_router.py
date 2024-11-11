from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.sale_post import SalePost
from app.schemas.sale_post_schema import SalePostCreate, SalePostResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

salePostRoutes = APIRouter()

# Crear un nuevo post de venta
@salePostRoutes.post('/sale-post/', status_code=status.HTTP_201_CREATED, response_model=SalePostResponse)
async def create_sale_post(sale_post: SalePostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_sale_post = SalePost(
        **sale_post.model_dump(exclude={'publication_date, seller_id'}),
        publication_date=datetime.now(),
        seller_id=current_user.id_user
    )
    db.add(db_sale_post)
    db.commit()
    return db_sale_post

# Obtener todos los posts de venta
@salePostRoutes.get('/sale-post/', response_model=List[SalePostResponse])
async def get_all_sale_posts(db: Session = Depends(get_db)):
    sale_posts = db.query(SalePost).all()
    return sale_posts

# Obtener un post de venta por su ID
@salePostRoutes.get('/sale-post/{id_sale_post}', response_model=SalePostResponse)
async def get_sale_post_by_id(id_sale_post: int, db: Session = Depends(get_db)):
    sale_post = db.query(SalePost).filter(SalePost.id_sale_post == id_sale_post).first()
    if not sale_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale post not found")
    return sale_post

# Actualizar un post de venta
@salePostRoutes.put('/sale-post/{id_sale_post}', response_model=SalePostResponse)
async def update_sale_post(id_sale_post: int, sale_post: SalePostCreate, db: Session = Depends(get_db)):
    db_sale_post = db.query(SalePost).filter(SalePost.id_sale_post == id_sale_post).first()
    if not db_sale_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale post not found")
    db_sale_post.title = sale_post.title
    db.commit()
    return db_sale_post

# Eliminar un post de venta
@salePostRoutes.delete('/sale-post/{id_sale_post}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale_post(id_sale_post: int, db: Session = Depends(get_db)):
    db_sale_post = db.query(SalePost).filter(SalePost.id_sale_post == id_sale_post).first()
    if not db_sale_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale post not found")
    db.delete(db_sale_post)
    db.commit()
    
    
