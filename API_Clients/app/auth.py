"""
This module generates a JWT for API Authentication
"""
from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from requests import session
from app.database import SessionLocal
from app.models import Customer
from pathlib import Path
import os
import bcrypt
import logging
import yaml

logger = logging.getLogger("auth")

def setup_logger():

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger



CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_PATH, "r",encoding="utf-8") as file_config:
    config = yaml.safe_load(file_config)
db_config = config["database"]
# Charger la configuration
ENV = os.getenv("APP_ENV", "dev")

if ENV == "test":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
elif ENV == "prod":
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
else:
    try:

        SQLALCHEMY_DATABASE_URL = (
            f"{db_config['engine']}://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config.get('port')}/{db_config['name']}"
        )
    except KeyError as e:
        raise RuntimeError(f"Champ manquant dans config.yaml : {e}")
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement de config.yaml : {e}")

jwt_config = config.get('jwt')
JWT_SECRET_KEY = jwt_config.get('secret_key')
JWT_ALGORITHM = jwt_config.get('algorithm')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config.get('access_token_expire_minutes')

engine = create_engine(SQLALCHEMY_DATABASE_URL)


def generate_jwt_token(payload: dict):
    data_to_encode = payload.copy()
    expire = datetime.now() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp": expire})
    token = jwt.encode(data_to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.debug(token)
    return token

def get_authenticated_user(username: str, password: str):
    Session  = sessionmaker(bind=engine)
    session = Session()
    user = session.query(Customer).where(Customer.username == username).first()
    logger.debug(f"User found: {user}")
    if not user:
        return False
    if not user.verify_password(password):
        return False
    logger.info("User authenticated")
    return user

def check_password(password_hash: str) -> bool:
    return bcrypt.checkpw(password_hash.encode('utf-8'), password_hash.encode('utf-8'))

def get_jwt_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token JWT manquant ou invalide")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token JWT invalide")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token JWT invalide")