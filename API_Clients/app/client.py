import requests


class APIClient:
    def __init__(self, base_url, api_key=None, bearer_token=None):
        """
        Initialise un client API avec l'URL de base et les informations d'authentification.

        :param base_url: URL de base de l'API (ex: "https://api.example.com ")
        :param api_key: Clé API (optionnelle)
        :param bearer_token: Token d'accès (optionnel)
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {}

        if api_key:
            self.headers["Authorization"] = f"Apikey {api_key}"
        elif bearer_token:
            self.headers["Authorization"] = f"Bearer {bearer_token}"

    def _make_url(self, endpoint):
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None):
        return requests.get(
            self._make_url(endpoint), headers=self.headers, params=params, timeout=5
        )

    def post(self, endpoint, json=None, data=None):
        return requests.post(
            self._make_url(endpoint), headers=self.headers, json=json, data=data, timeout=5
        )

    def put(self, endpoint, json=None, data=None):
        return requests.put(
            self._make_url(endpoint), headers=self.headers, json=json, data=data, timeout=5
        )

    def delete(self, endpoint):
        return requests.delete(self._make_url(endpoint), headers=self.headers, timeout=5)
