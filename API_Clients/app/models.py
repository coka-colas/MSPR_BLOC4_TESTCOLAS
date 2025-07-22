from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from app.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    actif = Column(Boolean, default=True)  # "actif" du JSON, stocké comme entier
    email = Column(String, unique=True, index=True)  # à ajouter si nécessaire
    password_hash = Column(String)

    #Méthodes pour hasher et vérifier le mot de passe
    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password_hash)
