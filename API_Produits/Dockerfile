FROM python:3.11-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier de dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Exposition du port utilisé par FastAPI
EXPOSE 8001

# Commande par défaut pour lancer l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]