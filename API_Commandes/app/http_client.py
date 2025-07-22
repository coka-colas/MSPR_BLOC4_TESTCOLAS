import httpx
import yaml
import os
from typing import Optional, Dict, Any
from app.logger import setup_logger

logger = setup_logger("http-client")

class ServiceConfig:
    def __init__(self):
        self.config = self._load_config()
        self.services = self._get_service_urls()
    
    def _load_config(self) -> dict:
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Config file not found, using defaults")
            return {}
    
    def _get_service_urls(self) -> dict:
        return {
            "products": os.getenv("PRODUCTS_SERVICE_URL", "http://localhost:8001"),
            "clients": os.getenv("CLIENTS_SERVICE_URL", "http://localhost:8002")
        }

class HTTPClient:
    def __init__(self):
        self.config = ServiceConfig()
        self.client = httpx.Client(timeout=30.0)
    
    async def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product information by ID from Products API"""
        try:
            url = f"{self.config.services['products']}/produits/{product_id}"
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    async def check_and_update_stock(self, product_id: int, quantity: int) -> bool:
        """Check stock availability and update if sufficient"""
        try:
            url = f"{self.config.services['products']}/produits/{product_id}/stock"
            data = {"quantity": quantity}
            response = self.client.patch(url, json=data)
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.error(f"Error updating stock for product {product_id}: {e}")
            return False
    
    async def validate_client_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate client token with Clients API"""
        try:
            url = f"{self.config.services['clients']}/api/clients/me"
            headers = {"Authorization": f"Bearer {token}"}
            response = self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    def close(self):
        self.client.close()

http_client = HTTPClient()