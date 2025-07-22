from sqlalchemy.orm import Session
from app.model import Product
from app.schema import ProduitCreate, ProduitUpdate

#Service pour créer un produit dans la base de données
def create_produit_in_db(db: Session, produit_data: ProduitCreate) -> Product:
    db_produit = Product(**produit_data.model_dump())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit

#Service pour récupérer la liste des produits dans la base de données
def get_produits(db: Session, skip: int, limit: int):
    query = db.query(Product)
    total = query.count()
    produits = query.offset(skip).limit(limit).all()
    return {"produits": produits, "total": total}

#Service pour récupérer un produit par son ID
def get_produit_by_id(db: Session, produit_id: int) -> Product:
    return db.query(Product).filter(Product.id == produit_id).first()

#Service pour mettre à jour un produit dans la base de données
def update_produit_in_db(
    db: Session, produit_id: int, update_data: ProduitUpdate
) -> Product:
    produit = db.query(Product).filter(Product.id == produit_id).first()
    if produit is None:
        raise ValueError("Product non trouvé")
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(produit, key, value)
    db.commit()
    db.refresh(produit)
    return produit

#Service pour supprimer un produit de la base de données
def delete_produit_from_db(db: Session, produit_id: int) -> bool:
    produit = db.query(Product).filter(Product.id == produit_id).first()
    if produit is None:
        return False
    db.delete(produit)
    db.commit()
    return True
