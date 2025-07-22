from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ProduitBase(BaseModel):
    """Schéma de base pour les produits."""

    name: str
    price: float
    description: str
    color: str
    stock: int


class ProduitCreate(ProduitBase):
    """Schéma pour la création d'un produit."""
    name: str
    price: float
    description: str
    color: str
    stock: int


class ProduitUpdate(BaseModel):
    """Schéma pour la mise à jour d'un produit."""

    name: str = None
    price: float = None
    description: str = None
    color: str = None
    stock: int = None


class ProduitResponse(ProduitBase):
    """Schéma pour les infos qui s'affichent quand on sélecionne un produit."""

    id: int
    createdAt: Optional[datetime] = None
    date_modification: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class ProduitList(BaseModel):
    """Schéma pour la liste totale des produits."""

    produits: List[ProduitResponse]
    total: int


class StockUpdateRequest(BaseModel):
    """Schéma pour la mise à jour du stock."""
    quantity: int


class StockUpdateResponse(BaseModel):
    """Schéma pour la réponse de mise à jour du stock."""
    product_id: int
    new_stock: int
    success: bool
