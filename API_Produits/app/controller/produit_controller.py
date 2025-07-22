from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.model import Product
from app.producer import RabbitMQProducer
from app.schema import ProduitCreate, ProduitUpdate
from app.service import produit_service

rabbitmq_producer = RabbitMQProducer()

#Création d'un produit
def create_produit(product: ProduitCreate, db: Session):
    existing = db.query(Product).filter(Product.name == product.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nom déjà utilisé")

    data = product.model_dump()
    db_product = Product(**data)

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    # Envoi du message à RabbitMQ
    try:
        rabbitmq_producer.publish_event("order_created", data)
        print("Message envoyé à RabbitMQ avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi à RabbitMQ : {e}")
    return db_product

# Récupération de la liste des produits
def list_produits(skip: int, limit: int, db: Session):
    return produit_service.get_produits(db, skip, limit)

# Récupération d'un produit par son ID
def get_produit(produit_id: int, db: Session):
    produit = produit_service.get_produit_by_id(db, produit_id)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit

# Mise à jour d'un produit
def update_produit(produit_id: int, produit_update: ProduitUpdate, db: Session):
    try:
        updated = produit_service.update_produit_in_db(db, produit_id, produit_update)
        # Envoi du message à RabbitMQ
        try:
            rabbitmq_producer.publish_event("product_updated", updated.__dict__)
            print("Message envoyé à RabbitMQ (update) avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi à RabbitMQ (update) : {e}")
        return updated
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Nom déjà utilisé") from exc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Suppression d'un produit
def delete_produit(produit_id: int, db: Session):
    if not produit_service.delete_produit_from_db(db, produit_id):
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    # Envoi du message à RabbitMQ
    try:
        rabbitmq_producer.publish_event("order_deleted", {"order_id": produit_id})
        print("Message envoyé à RabbitMQ (delete) avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi à RabbitMQ (delete) : {e}")

# Mise à jour du stock d'un produit
def update_stock(produit_id: int, new_stock: int, db: Session):
    produit = db.query(Product).filter(Product.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    produit.stock = new_stock
    db.commit()
    db.refresh(produit)
    return produit