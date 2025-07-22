from sqlalchemy.orm import Session
from app.models import Customer
from app.schema import ClientCreate, ClientUpdate

# Service pour la création d'un client dans la base de données
def create_client_in_db(db: Session, client_data: ClientCreate) -> Customer:
    db_client = Customer(**client_data.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# Service pour obtenir la liste des clients avec pagination et filtrage
def get_clients(db: Session, skip: int, limit: int, actif: bool = None):
    query = db.query(Customer)
    if actif is not None:
        query = query.filter(Customer.actif == actif)
    total = query.count()
    clients = query.offset(skip).limit(limit).all()
    return {"clients": clients, "total": total}

# Service pour obtenir un client par son ID
def get_client_by_id(db: Session, client_id: int) -> Customer:
    return db.query(Customer).filter(Customer.id == client_id).first()

# Service pour mettre à jour un client dans la base de données
def update_client_in_db(
    db: Session, client_id: int, update_data: ClientUpdate
) -> Customer:
    client = db.query(Customer).filter(Customer.id == client_id).first()
    if client is None:
        raise ValueError("Customer non trouvé")
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return client

# Service pour supprimer un client de la base de données
def delete_client_from_db(db: Session, client_id: int) -> bool:
    client = db.query(Customer).filter(Customer.id == client_id).first()
    if client is None:
        return False
    db.delete(client)
    db.commit()
    return True
