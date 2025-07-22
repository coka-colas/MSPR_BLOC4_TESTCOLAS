#Fichier qui contient les fonctions utilitaires pour l'authentification
# et la création de tokens JWT
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta
import secrets

JWT_SECRET = secrets.token_hex(32)
JWT_ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt