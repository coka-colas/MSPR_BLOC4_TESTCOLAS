from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ClientBase(BaseModel):
    """Schéma de base pour les clients."""

    nom: str = Field(..., min_length=2, max_length=50)
    prenom: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=8, max_length=15)
    actif: bool = True

#Schema pour la création d'un client
class ClientCreate(BaseModel):
    username: str
    name: str
    first_name: str
    last_name: str
    postal_code: str
    city: str
    profile_first_name: str
    profile_last_name: str
    company_name: str
    email: str
    phone: str
    actif: bool
    password: str

#Schema pour la mise à jour d'un client
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

#Schema pour la réponse d'un client
class ClientResponse(BaseModel):
    username: str
    name: str
    first_name: str
    last_name: str
    postal_code: str
    city: str
    profile_first_name: str
    profile_last_name: str
    company_name: str
    email: str
    phone: str
    actif: bool


class ClientList(BaseModel):
    """Schéma pour la liste des clients."""

    clients: List[ClientResponse]
    total: int

# Schema pour la requête de connexion
class LoginRequest(BaseModel):
    username: str
    password: str
