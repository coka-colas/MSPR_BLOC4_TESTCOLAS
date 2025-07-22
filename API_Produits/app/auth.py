"""
JWT authentication for API_Produits
"""
import httpx
import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.clients_service_url = os.getenv("CLIENTS_SERVICE_URL", "http://localhost:8002")
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token with the Clients service"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(f"{self.clients_service_url}/api/clients/me", headers=headers)
                if response.status_code == 200:
                    return response.json()
                return None
        except httpx.HTTPError:
            return None

auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    user_info = await auth_service.validate_token(credentials.credentials)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_info

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    return await auth_service.validate_token(credentials.credentials)