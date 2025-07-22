import requests

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Customer
from app.schema import ClientCreate, ClientUpdate
from app.service import client_service
from app.producer import RabbitMQProducer


#Création d'un client
def create_client(client: ClientCreate, db: Session):
    rabbitmq_producer = RabbitMQProducer()
    existing = db.query(Customer).filter(Customer.email == client.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    data = client.model_dump()
    password = data.pop("password")  # On retire le champ password
    db_client = Customer(**data)
    db_client.set_password(password)  # Méthode définie dans le modèle

    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    # Envoi du message à RabbitMQ
    try:
        rabbitmq_producer.publish_event("client.created", data)
        print("Message envoyé à RabbitMQ avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi à RabbitMQ : {e}")
    return db_client

#Liste des clients
def list_clients(skip: int, limit: int, actif: bool, db: Session):
    return client_service.get_clients(db, skip, limit, actif)

#Obtenir les informations d'un client
def get_client(client_id: int, db: Session):
    client = client_service.get_client_by_id(db, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client

#Mise à jour d'un client
def update_client(client_id: int, client_update: ClientUpdate, db: Session):
    rabbitmq_producer = RabbitMQProducer()
    try:
        updated = client_service.update_client_in_db(db, client_id, client_update)
        # Envoi du message à RabbitMQ
        try:
            rabbitmq_producer.publish_event("client.updated", updated.__dict__)
            print("Message envoyé à RabbitMQ (update) avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi à RabbitMQ (update) : {e}")
        return updated
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Email déjà utilisé") from exc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

#Suppression d'un client
def delete_client(client_id: int, db: Session):
    rabbitmq_producer = RabbitMQProducer()
    if not client_service.delete_client_from_db(db, client_id):
        raise HTTPException(status_code=404, detail="Client non trouvé")
    # Envoi du message à RabbitMQ
    try:
        rabbitmq_producer.publish_event("client.deleted", {"client_id": client_id})
        print("Message envoyé à RabbitMQ (delete) avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi à RabbitMQ (delete) : {e}")

#Obtenir un client par son nom d'utilisateur
def get_client_by_username(username: str, db: Session):
    client = db.query(Customer).filter(Customer.username == username).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client
