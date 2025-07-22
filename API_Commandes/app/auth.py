#Fichier qui gère l'authentification des utilisateurs via JWT
from fastapi import Request, HTTPException
from jose import jwt, JWTError
from functools import wraps
from typing import Callable
from sqlalchemy.orm import Session
from app.model import Customer
from app.database import get_db

SECRET_KEY = "ton_secret_ici"
ALGORITHM = "HS256"

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expiré ou invalide")

async def auth_middleware(request: Request, call_next: Callable):
    excluded_paths = ["/docs", "/openapi.json", "/clients"]  # On autorise la création de client sans token

    if request.url.path in excluded_paths:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")

    token = auth_header.split(" ")[1]

    try:
        payload = decode_token(token)
        email = payload.get("sub")
        # Cherche l'utilisateur dans la base via l'email
        db = next(get_db())
        user = db.query(Customer).filter(Customer.email == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur inconnu")

        request.state.user = user  # Stocke l'utilisateur pour les endpoints
        current_user = request.state.user
        user_id = current_user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentification échouée")

    return await call_next(request)

# New authentication functions for dependency injection
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.http_client import http_client

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user by validating token with Clients API"""
    user_info = await http_client.validate_client_token(credentials.credentials)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_info

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    return await http_client.validate_client_token(credentials.credentials)