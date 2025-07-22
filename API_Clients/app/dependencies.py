import os
import yaml

from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional

from app.auth import JWT_SECRET_KEY, JWT_ALGORITHM, get_jwt_current_user

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml')
with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/clients/login")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant utilisateur manquant dans le token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = get_jwt_current_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def check_role(required_role: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") == required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Rôle '{required_role}' requis"
        )
    return True