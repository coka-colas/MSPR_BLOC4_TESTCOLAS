FROM python:3.13-alpine

# Répertoire de travail dans le conteneur
WORKDIR /app

# Installer curl et dépendances Alpine
RUN apk add --no-cache curl gcc musl-dev postgresql-dev

# Copie du fichier de dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple --default-timeout=100

ENV PYTHONPATH=/app

# Exposition du port utilisé par FastAPI (plus utilsé car il se trouve dans le docker-compose)
#EXPOSE 8000

# Commande par défaut pour lancer l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]