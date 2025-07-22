from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import json
from typing import Dict, Any
from app.controller import order_controller
from app.database import get_db
from app.schema import OrderCreate, OrderResponse, OrderUpdate, OrderList
from app.logger import setup_logger
from app.http_client import http_client
from app.auth import get_current_user

logger = setup_logger("api-service")
router = APIRouter(prefix="/orders", tags=["orders"])

#Route pour la création d'une commande
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    logger.info(f"Création d'une nouvelle commande pour l'utilisateur {current_user.get('username')}")
    
    # Vérifier que l'utilisateur crée une commande pour lui-même
    if order.customer_id != current_user.get('id'):
        raise HTTPException(status_code=403, detail="Vous ne pouvez créer une commande que pour votre propre compte")
    
    # Valider et réserver le stock pour chaque produit
    for item in order.items:
        # Vérifier que le produit existe et qu'il y a suffisamment de stock
        product = await http_client.get_product_by_id(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Produit {item.product_id} non trouvé")
        
        # Vérifier et mettre à jour le stock
        stock_updated = await http_client.check_and_update_stock(item.product_id, item.quantity)
        if not stock_updated:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuffisant pour le produit {item.product_id}"
            )
    
    # Créer la commande
    new_order = order_controller.create_order(order, db)
    logger.info(f"Commande créée avec succès: {new_order.order_id}")
    return new_order

#Route pour la liste des commandes (pour les admins)
@router.get("/", response_model=OrderList)
async def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return order_controller.list_orders(skip, limit, db)

#Route pour l'historique des commandes d'un client
@router.get("/my-orders", response_model=OrderList)
async def get_my_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Récupère l'historique des commandes pour le client connecté"""
    logger.info(f"Récupération de l'historique des commandes pour l'utilisateur {current_user.get('username')}")
    return order_controller.get_orders_by_customer(current_user.get('id'), skip, limit, db)

#Route pour obtenir une commande par son ID
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return order_controller.get_order(order_id, db)

#Route pour mettre à jour une commande
@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    logger.info("Mise à jour d'une commande")
    updated = order_controller.update_order(order_id, order_update, db)
    return updated

#Route pour supprimer une commande
@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    logger.info("Suppression d'une commande")
    order_controller.delete_order(order_id, db)
