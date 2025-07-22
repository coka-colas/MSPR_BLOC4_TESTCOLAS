from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schema import OrderCreate, OrderUpdate
from app.service import order_service

#Création d'une commande
def create_order(order_data: OrderCreate, db: Session):
    try:
        new_order = order_service.create_order_in_db(db, order_data)
        return new_order
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur de création de la commande."
        )

#Lister l'ensemble des commandes
def list_orders(skip: int, limit: int, db: Session):
    return order_service.get_orders(db, skip, limit)

#Obtenir une commande par son ID
def get_order(order_id: int, db: Session):
    order = order_service.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order

#Mettre à jour une commande
def update_order(order_id: int, order_update: OrderUpdate, db: Session):
    try:
        updated = order_service.update_order_in_db(db, order_id, order_update)
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Conflit lors de la mise à jour")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

#Supprimer une commande
def delete_order(order_id: int, db: Session):
    if not order_service.delete_order_from_db(db, order_id):
        raise HTTPException(status_code=404, detail="Commande non trouvée")

#Obtenir les commandes d'un client spécifique
def get_orders_by_customer(customer_id: int, skip: int, limit: int, db: Session):
    return order_service.get_orders_by_customer(db, customer_id, skip, limit)
