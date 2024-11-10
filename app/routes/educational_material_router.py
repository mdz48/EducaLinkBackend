from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
from app.models.educational_material import EducationalMaterial
from app.schemas.educational_material_schema import EducationalMaterialCreate, EducationalMaterialResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

educationalMaterialRoutes = APIRouter()

# Crear un nuevo material educativo
@educationalMaterialRoutes.post('/educational-material/', status_code=status.HTTP_201_CREATED, response_model=EducationalMaterialResponse)
async def create_educational_material(educational_material: EducationalMaterialCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_educational_material = EducationalMaterial(**educational_material.model_dump(exclude={'publication_date'}), publication_date=datetime.now(), user_id=current_user.id_user)
    db.add(db_educational_material)
    db.commit()
    return db_educational_material

# Obtener materiales educativos por ID de usuario
@educationalMaterialRoutes.get('/educational-material/user/{user_id}', response_model=List[EducationalMaterialResponse])
async def get_educational_materials_by_user(user_id: int, db: Session = Depends(get_db)):
    educational_materials = db.query(EducationalMaterial).filter(EducationalMaterial.user_id == user_id).all()
    return educational_materials

# Obtener materiales educativos por ID de categoría
@educationalMaterialRoutes.get('/educational-material/category/{category_id}', response_model=List[EducationalMaterialResponse])
async def get_educational_materials_by_category(category_id: int, db: Session = Depends(get_db)):
    educational_materials = db.query(EducationalMaterial).filter(EducationalMaterial.category_id == category_id).all()
    return educational_materials

# Obtener un material educativo por su ID
@educationalMaterialRoutes.get('/educational-material/{id_material}', response_model=EducationalMaterialResponse)
async def get_educational_material_by_id(id_material: int, db: Session = Depends(get_db)):
    educational_material = db.query(EducationalMaterial).filter(EducationalMaterial.id_material == id_material).first()
    if not educational_material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Educational material not found")
    return educational_material

# Actualizar un material educativo por su ID
@educationalMaterialRoutes.put('/educational-material/{id_material}', response_model=EducationalMaterialResponse)
async def update_educational_material(id_material: int, educational_material: EducationalMaterialCreate, db: Session = Depends(get_db)):
    db_educational_material = db.query(EducationalMaterial).filter(EducationalMaterial.id_material == id_material).first()
    if not db_educational_material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Educational material not found")
    db_educational_material.title = educational_material.title
    db.commit()
    return db_educational_material

# Eliminar un material educativo por su ID
@educationalMaterialRoutes.delete('/educational-material/{id_material}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_educational_material(id_material: int, db: Session = Depends(get_db)):
    db.query(EducationalMaterial).filter(EducationalMaterial.id_material == id_material).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


