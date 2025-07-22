from fastapi import APIRouter, Depends, HTTPException, Request, status

from sqlalchemy.orm import Session
from app.controller import client_controller
from app.database import get_db
from app.dependencies import check_role
from app.schema import ClientCreate, ClientList, ClientResponse, ClientUpdate, LoginRequest
from app.auth import generate_jwt_token, get_authenticated_user, get_jwt_current_user

router = APIRouter(tags=["Clients"])

# ----------------------
# Routes publiques
# ----------------------

from fastapi import APIRouter, Depends

#Routes publiques pour l'authentification
@router.post("/login")
def login(request: LoginRequest):
    username = request.username
    password = request.password
    user = get_authenticated_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    access_token = generate_jwt_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

#Routes pour vérifier le rôle de l'utilisateur
def get_role_checker(required_role: str):
    def role_dependency(request: Request):
        result = check_role(required_role, request)
        if not result:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")
        return result
    return role_dependency

check_admin = get_role_checker("admin")
check_user = get_role_checker("user")
''', dependencies=[Depends(check_admin)] 
+ ,api_key: str = Depends(verify_api_key)
 à ajouter une fois que le tests des routes soit validés.'''

# Route POST /api/clients => création d'un client
@router.post("/", response_model=ClientResponse)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    return client_controller.create_client(client, db)

# Route GET /api/clients/=> Obtenir la liste des clients
@router.get("/", response_model=ClientList,  dependencies=[Depends(check_admin)])
def list_clients(skip: int = 0, limit: int = 10, actif: bool = True, db: Session = Depends(get_db)):
    return client_controller.list_clients(skip,limit,actif,db)

# Route GET /api/clients/{client_id} => Obtenir les informations d'un client
@router.get("/{client_id}", response_model=ClientResponse, dependencies=[Depends(check_admin)])
def get_client(client_id: int, db: Session = Depends(get_db)):
    return client_controller.get_client(client_id, db)

# Route PUT /api/clients/{client_id} => Mise à jour d'un client
@router.put("/{client_id}", response_model=ClientResponse, dependencies=[Depends(check_admin)])
def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    return client_controller.update_client(client_id, client_update, db)

# Route DELETE /api/clients/{client_id} => Suppression d'un client
@router.delete("/{client_id}", status_code=204, dependencies=[Depends(check_admin)])
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client_controller.delete_client(client_id, db)
    return None

# Route GET /api/clients/me => Obtenir le profil du client connecté
@router.get("/me", response_model=ClientResponse)
def get_my_profile(current_user: dict = Depends(get_jwt_current_user), db: Session = Depends(get_db)):
    return client_controller.get_client_by_username(current_user.get("sub"), db)