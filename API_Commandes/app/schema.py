from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


#Table et ensemble des opérations liés à un produit
class Product(BaseModel):
    id: Optional[int]
    name: str
    stock: int
    price: str
    description: str
    color: str

    class Config:
        validate_by_name = True
        from_attributes = True

# Produit pour création (client → API)
class ProductCreate(BaseModel):
    name: str
    stock: int
    price: str
    description: str
    color: str



#Table et ensemble des opérations liés à une commande
class Order(BaseModel):
    orderId: Optional[int] = Field(None, alias="order_id")
    customerId: int = Field(..., alias="customer_id")
    createdAt: Optional[datetime] = Field(None, alias="created_at")
    products: List[Product] = []
    class Config:
        validate_by_name = True
        from_attributes = True
        populate_by_name = True


class OrderItem(BaseModel):
    """Schéma pour un article dans une commande"""
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItem]

    class Config:
        from_attributes = True

# Commande pour mise à jour
class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    product_ids: List[int]

    class Config:
        from_attributes = True

# Pour récupérer une commande
class OrderResponse(Order):
    pass

# Pour obtenir la liste des commandes
class OrderList(BaseModel):
    orders: List[Order]
    total: int

    class Config:
        from_attributes = True