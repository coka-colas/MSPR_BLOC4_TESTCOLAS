from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.router.produit_router import router as produit_router
from app import model

# Création des tables dans la base de données
model.Base.metadata.create_all(bind=engine)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Produit API", description="API pour la gestion des produits", version="1.0.0"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initialisation de l'application...")
    if os.getenv("APP_ENV") == "test":
        from app.database import init_db
        init_db()
    yield
    print("Fermeture de l'application...")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(produit_router)


@app.get("/")
def read_root():
    """Endpoint racine de l'API."""
    return {"message": "Bienvenue sur l'API de gestion des produits"}

# Endpoint de santé
@app.get("/health")
def health_check():
    return {"status": "healthy"}
