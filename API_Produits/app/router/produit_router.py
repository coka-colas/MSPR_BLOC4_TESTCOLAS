from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import json
from typing import Dict, Any, Optional
from app import producer
from app.controller import produit_controller
from app.database import get_db
from app.schema import ProduitCreate, ProduitResponse, ProduitUpdate, ProduitList, StockUpdateRequest, StockUpdateResponse
from app.logger import setup_logger
from app.auth import get_current_user

logger = setup_logger("api-service")
router = APIRouter(prefix="/produits", tags=["produits"])

# Routing Key :
# Produit créé : produit.created
# produit supprimé : produit.deleted
# produit modifié : produit.updated

#Route pour créer un produit
@router.post("/", response_model=ProduitResponse, status_code=status.HTTP_201_CREATED)
def create_produit(
    produit: ProduitCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    logger.info("Création d'un nouveau produit")
    nouveau_produit = produit_controller.create_produit(produit, db)
    produit_pydantic = ProduitResponse.model_validate(nouveau_produit)
    
    background_tasks.add_task(
    producer.envoyer_message,
    routing_key="produit.created",
    body=produit_pydantic.model_dump_json()
    )

    return nouveau_produit

#Route pour lister les produits (nécessite authentification)
@router.get("/", response_model=ProduitList)
async def list_produits(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return produit_controller.list_produits(skip, limit, db)

#Route pour récupérer un produit par son ID
@router.get("/{produit_id}", response_model=ProduitResponse)
def get_produit(produit_id: int, db: Session = Depends(get_db)):
    return produit_controller.get_produit(produit_id, db)

#Route pour mettre à jour un produit
@router.put("/{produit_id}", response_model=ProduitResponse)
def update_produit(
    produit_id: int, produit_update: ProduitUpdate, db: Session = Depends(get_db)
):
    logger.info("Mise à jour des informations d'un produit")
    produit_update = produit_controller.update_produit(produit_id, produit_update, db)

    producer.envoyer_message(
        routing_key="produit_updated", body=produit_update.model_dump_json()
    )

#Route pour supprimer un produit
@router.delete("/{produit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produit(produit_id: int, db: Session = Depends(get_db)):
    logger.info("Suppression d'un produit")
    produit = produit_controller.delete_produit(produit_id, db)

    producer.envoyer_message(
        routing_key="produit.deleted", body=json.dumps({"produit_id": produit_id})
    )

    return None


# Route pour vérifier et mettre à jour le stock
@router.patch("/{produit_id}/stock", response_model=StockUpdateResponse)
async def update_stock(
    produit_id: int, 
    stock_request: StockUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour vérifier et décrémenter le stock d'un produit.
    Utilisé par l'API_Commandes lors de la création d'une commande.
    """
    logger.info(f"Demande de mise à jour du stock pour le produit {produit_id}, quantité: {stock_request.quantity}")
    
    # Récupérer le produit
    produit = produit_controller.get_produit(produit_id, db)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier si le stock est suffisant
    if produit.stock < stock_request.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Stock insuffisant. Stock disponible: {produit.stock}, demandé: {stock_request.quantity}"
        )
    
    # Mettre à jour le stock
    new_stock = produit.stock - stock_request.quantity
    produit_controller.update_stock(produit_id, new_stock, db)
    
    return StockUpdateResponse(
        product_id=produit_id,
        new_stock=new_stock,
        success=True
    )
