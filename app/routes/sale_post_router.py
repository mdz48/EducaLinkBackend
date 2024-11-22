from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.models.interfaces import PostStatus
from app.models.sale_post import SalePost
from app.schemas.sale_post_schema import SalePostCreate, SalePostResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user
from sqlalchemy.orm import joinedload
import time
import boto3
import os
from dotenv import load_dotenv
import time

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

salePostRoutes = APIRouter()

# Crear un nuevo post de venta
@salePostRoutes.post('/sale-post/', status_code=status.HTTP_201_CREATED, response_model=SalePostResponse, tags=["Posts de venta"])
async def create_sale_post(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    type: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):

    # Subir imagen a S3
    image_key = f"{int(time.time())}_{image.filename}"
    s3.upload_fileobj(image.file, 'educalinkbucket', image_key, ExtraArgs={'ContentType': image.content_type})
    image_url = f"https://educalinkbucket.s3.amazonaws.com/{image_key}"
    # Raise si no se pudo subir la imagen
    if not image_url:
        raise HTTPException(status_code=500, detail="Error subiendo la imagen")
    
    db_sale_post = SalePost(
        title=title,
        description=description,
        price=price,
        publication_date=datetime.now(),
        sale_type=type,
        seller_id=current_user.id_user,
        status='Disponible',
        image_url = image_url
    )

    db.add(db_sale_post)
    db.commit()
    
    # Guardar la URL de la imagen en el post
    db_sale_post.image_url = image_url  # Asignar la URL de la imagen al campo image_url

    db.commit()  # Asegúrate de hacer commit después de agregar el post

    return SalePostResponse(
        id_sale_post=db_sale_post.id_sale_post,
        title=db_sale_post.title,
        description=db_sale_post.description,
        price=db_sale_post.price,
        sale_type=db_sale_post.sale_type,
        image_url=db_sale_post.image_url,  # Incluir la URL de la imagen
        publication_date=db_sale_post.publication_date,
        status=db_sale_post.status,
        seller=db_sale_post.seller
    )

# Obtener todos los posts de venta
@salePostRoutes.get('/sale-post/', response_model=List[SalePostResponse], tags=["Posts de venta"])
async def get_all_sale_posts(db: Session = Depends(get_db)):
    # Obtener al usuario de la venta
    sale_posts = db.query(SalePost).options(joinedload(SalePost.seller)).all()
    return sale_posts

# Obtener un post de venta por su ID
@salePostRoutes.get('/sale-post/{id_sale_post}', response_model=SalePostResponse, tags=["Posts de venta"])
async def get_sale_post_by_id(id_sale_post: int, db: Session = Depends(get_db)):
    sale_post = db.query(SalePost).filter(SalePost.id_sale_post == id_sale_post).first()
    if not sale_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale post not found")
    return SalePostResponse(
        id_sale_post=sale_post.id_sale_post,
        title=sale_post.title,
        description=sale_post.description,
        price=sale_post.price,
        image_url=sale_post.image_url,
        publication_date=sale_post.publication_date,
        status=sale_post.status,
        seller=sale_post.seller
    )

# Actualizar un post de venta
@salePostRoutes.put('/sale-post/{id_sale_post}', response_model=SalePostResponse, tags=["Posts de venta"])
async def update_sale_post(id_sale_post: int, sale_post: SalePostCreate, db: Session = Depends(get_db)):
    db_sale_post = db.query(SalePost).filter(SalePost.id_sale_post == id_sale_post).first()
    if not db_sale_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale post not found")
    db_sale_post.title = sale_post.title
    db.commit()
    return db_sale_post

# Eliminar un post de venta
@salePostRoutes.delete('/sale-post/{id_sale_post}', status_code=status.HTTP_204_NO_CONTENT, tags=["Posts de venta"])
async def delete_sale_post(id_sale_post: int, db: Session = Depends(get_db)):
    db_sale_post = db.query(SalePost).filter(SalePost.id_sale_post == id_sale_post).first()
    if not db_sale_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale post not found")
    db.delete(db_sale_post)
    db.commit()
    
# Obtener post por su tipo 
@salePostRoutes.get('/sale-post/type/{sale_type}', response_model=List[SalePostResponse], tags=["Posts de venta"])
async def get_sale_post_by_type(sale_type: str, db: Session = Depends(get_db)):
    sale_posts = db.query(SalePost).filter(SalePost.sale_type == sale_type).all()
    return [
        SalePostResponse(
            id_sale_post=sale_post.id_sale_post,
            title=sale_post.title,
            description=sale_post.description,
            price=sale_post.price,
            image_url=sale_post.image_url,
            publication_date=sale_post.publication_date,
            status=sale_post.status,
            seller=sale_post.seller
        )
        for sale_post in sale_posts
    ]


# Obtener posts de venta por el usuario que lo vende
@salePostRoutes.get('/sale-post/user/{user_id}', response_model=List[SalePostResponse], tags=["Posts de venta"])
async def get_sale_post_by_user_available(user_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    sale_posts = db.query(SalePost).filter(SalePost.seller_id == user_id, SalePost.status == 'Disponible').all()
    
    return sale_posts

# Cambiar el estado de un post de venta
@salePostRoutes.put('/sale-post/{id_sale_post}/status', response_model=SalePostResponse, tags=["Posts de venta"])
async def change_sale_post_status(id_sale_post: int, status: PostStatus, db: Session = Depends(get_db)):
    db_sale_post = db.query(SalePost).filter(SalePost.id_sale_post == id_sale_post).first()
    if not db_sale_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale post not found")
    db_sale_post.status = status
    db.commit()
    return db_sale_post