from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.security import APIKeyHeader
from app.routers.client_router import router

import os

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initialisation de l'application...")
    from app.database import init_db
    init_db()
    yield
    print("Fermeture de l'application...")

app = FastAPI(
    title="Client API",
    description="API Clients avec FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Inclusion des routeurs
app.include_router(router, prefix="/api/clients")

# Middleware JWT
#app.middleware("http")(auth_middleware)

# Middleware pour clé API
#@app.middleware("http")
#async def api_key_middleware(request: Request, call_next):
#    verify_api_key(request)
#    return await call_next(request)



# Endpoint de santé
@app.get("/health")
def health_check():
    return {"status": "healthy"}