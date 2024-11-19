from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from app.shared.config.db import Base
from app.models.interfaces import PostStatus, SaleType
from app.models.User import User  # Asegúrate de importar el modelo User


class SalePost(Base):
    __tablename__ = "sale_posts"
    id_sale_post = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(Text, nullable=True)
    publication_date = Column(DateTime, nullable=False)
    sale_type = Column(Enum(SaleType), nullable=False)
    status = Column(Enum(PostStatus), nullable=True, default=PostStatus.Disponible)
    seller_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Definir la relación con el modelo User
    seller = relationship("User", back_populates="sale_posts")  # Asegúrate de que 'User' tenga la relación inversa

