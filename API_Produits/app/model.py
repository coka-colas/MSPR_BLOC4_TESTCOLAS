from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

#Modèle de données pour les produits
class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    color = Column(String)
    stock = Column(Integer)
