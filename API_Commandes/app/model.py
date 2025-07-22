from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Table d'association many-to-many
order_products = Table(
    "order_products",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.order_id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True)
)

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship(
        "Product",
        secondary=order_products,
        back_populates="orders"
    )

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)# "name" du JSON
    stock = Column(Integer)# "stock" du JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())# "createdAt" du JSON
    price = Column(String)# "price" du JSON
    description = Column(String)# "description" du JSON
    color = Column(String)# "color" du JSON

    orders = relationship(
        "Order",
        secondary=order_products,
        back_populates="products"
    )

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # "username" du JSON
    name = Column(String, index=True)      # "name" du JSON
    first_name = Column(String, index=True)  # "firstName" du JSON
    last_name = Column(String, index=True)   # "lastName" du JSON
    postal_code = Column(String, index=True) # "address.postalCode" du JSON
    city = Column(String, index=True)        # "address.city" du JSON
    profile_first_name = Column(String, index=True)  # "profile.firstName"
    profile_last_name = Column(String, index=True)   # "profile.lastName"
    company_name = Column(String, index=True)        # "company.companyName"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    phone = Column(String, index=True)  # "phone" du JSON
    actif = Column(Integer, default=1)  # "actif" du JSON, stocké comme entier
    email = Column(String, unique=True, index=True)  # à ajouter si nécessaire
    password_hash = Column(String)

    #Méthodes pour hasher et vérifier le mot de passe
    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password_hash)
