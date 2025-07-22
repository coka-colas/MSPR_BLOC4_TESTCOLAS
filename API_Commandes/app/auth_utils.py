#Fichier qui contient les fonctions utilitaires pour l'authentification
# et la création de tokens JWT
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "ton_secret_ici"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt