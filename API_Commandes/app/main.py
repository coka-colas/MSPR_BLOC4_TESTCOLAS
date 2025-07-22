import asyncio
from contextlib import asynccontextmanager
from threading import Thread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import start_http_server, Counter, Histogram


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from app.database import engine
from app.router.order_router import router as order_router
from app import model
from app.consumer import demarrer_consumer

# Variable globale pour le thread
listener_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application."""
    global listener_thread
    
    # STARTUP
    logger.info("Démarrage de l'application...")

    try:
        # Démarrer le consumer RabbitMQ dans un thread
        listener_thread = Thread(
            target=traiter_evenement_wrapper,
            daemon=True,
            name="RabbitMQ-Consumer"
        )
        listener_thread.start()
        logger.info("✅ Thread RabbitMQ démarré")
        logger.info("🎉 Application démarrée")

    except Exception as e:
        logger.error(f"❌ Erreur startup: {e}")
        raise

    # L'APPLICATION TOURNE ICI
    yield
    
    # 🔄 SHUTDOWN
    logger.info("🔄 Arrêt de l'application...")
    
    # Le thread daemon s'arrêtera automatiquement avec l'app
    if listener_thread and listener_thread.is_alive():
        logger.info("🔄 Thread RabbitMQ en cours d'arrêt...")
    
    logger.info("👋 Application stopped")

def traiter_evenement_wrapper():
    """Wrapper sécurisé pour votre fonction de traitement."""
    try:
        demarrer_consumer()
    except Exception as e:
        logger.error(f"💥 Erreur critique dans le listener: {e}")

# Créer l'app avec lifespan correctement
app = FastAPI(
    title="Commande API",
    description="API pour la gestion des commandes",
    version="1.0.0",
    lifespan=lifespan
)

# Création des tables dans la base de données
model.Base.metadata.create_all(bind=engine)

# Inclusion des routes
app.include_router(order_router)

#Route Racine de l'api 
@app.get("/")
def read_root():
    """Endpoint racine de l'API."""
    return {"message": "Bienvenue sur l'API de gestion des commandes"}

#Permet de vérifier que l'API est démarrée et que le listener RabbitMQ fonctionne
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "rabbitmq_consumer": "running" if listener_thread and listener_thread.is_alive() else "stopped"
    }

