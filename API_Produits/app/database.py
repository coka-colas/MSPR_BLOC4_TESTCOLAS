import os
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Charger la configuration
ENV = os.getenv("APP_ENV", "dev")

if ENV == "test":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
elif ENV == "prod":
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
else:
    try:
        with open("config.yaml", "r", encoding="utf-8") as file_config:
            config = yaml.safe_load(file_config)
        db_config = config["database"]
        SQLALCHEMY_DATABASE_URL = (
            f"{db_config['engine']}://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config.get('port')}/{db_config['name']}"
        )
    except KeyError as e:
        raise RuntimeError(f"Champ manquant dans config.yaml : {e}")
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement de config.yaml : {e}")

# Création du moteur SQLAlchemy
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
except Exception as e:
    raise RuntimeError(f"Échec de création du moteur SQLAlchemy : {e}")

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_engine(database_url: str = None):
    """Permet de créer un moteur personnalisé (pour les tests)"""
    return create_engine(
        database_url or SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

def get_db():
    """Obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_db_connection():
    """Tester la connexion à la base de données"""
    try:
        engine.connect()
        print("Connexion à la base réussie.")
    except Exception as e:
        print(f"Échec de la connexion à la base : {e}")

def init_db():
    """Initialiser les tables si on n'est pas en mode test"""
    if os.getenv("APP_ENV") != "test":
        from app.model import Customer  # Import tardif pour éviter les cycles
        Base.metadata.create_all(bind=engine)
        print("Base de données initialisée.")
