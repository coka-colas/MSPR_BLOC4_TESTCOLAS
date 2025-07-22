from sqlalchemy import select
from sqlalchemy.orm import Session 
from app.model import Order, Product, order_products
from app.schema import OrderCreate, OrderUpdate

#Service pour créer une commande
def create_order_in_db(db: Session, order_data: OrderCreate) -> Order:
    order_dict = order_data.model_dump()
    items = order_dict.pop("items", [])
    product_ids = [item["product_id"] for item in items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    db_order = Order(customer_id=order_data.customer_id)
    db_order.products = products
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

#Service pour lister les commandes
def get_orders(db: Session, skip: int, limit: int):
    total = db.query(Order).count()
    orders = db.query(Order).offset(skip).limit(limit).all()
    return {"orders": orders, "total": total}

#Service pour obtenir une commande par son ID
def get_order_by_id(db: Session, order_id: int) -> Order:
    return db.query(Order).filter(Order.order_id== order_id).first()

#Service pour mettre à jour une commande
def update_order_in_db(db: Session, order_id: int, update_data: OrderUpdate):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order is None:
        raise ValueError("Commande non trouvée")
    update_dict = update_data.model_dump(exclude_unset=True)
    # Met à jour les champs simples
    for key, value in update_dict.items():
        if key != "product_ids":
            setattr(order, key, value)
    # Met à jour la liste des produits si besoin
    if "product_ids" in update_dict:
        products = db.query(Product).filter(Product.id.in_(update_dict["product_ids"])).all()
        order.products = products
    db.commit()
    db.refresh(order)
    # On retourne le corps simplifié
    return order

#Service pour supprimer une commande
def delete_order_from_db(db: Session, order_id: int) -> bool:
    order = db.query(Order).filter(Order.order_id== order_id).first()
    if order is None:
        return False
    db.delete(order)
    db.commit()
    return True

#Service pour obtenir les commandes d'un client spécifique
def get_orders_by_customer(db: Session, customer_id: int, skip: int, limit: int):
    total = db.query(Order).filter(Order.customer_id == customer_id).count()
    orders = db.query(Order).filter(Order.customer_id == customer_id).offset(skip).limit(limit).all()
    return {"orders": orders, "total": total}
