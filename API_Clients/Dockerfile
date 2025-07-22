FROM python:3.13-alpine

#Répertoire de travail dans le conteneur
WORKDIR /app

# Installe les dépendances système
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-libs \
    libffi-dev

# Copie des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


ENV PYTHONPATH=/app

# Expose le port FastAPI
#EXPOSE 8002

# Commande par défaut pour lancer l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]