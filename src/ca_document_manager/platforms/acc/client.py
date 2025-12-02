# Source: src\ca_document_manager\platforms\acc\client.py
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class Client:
    BASE_URL: str = "https://developer.api.autodesk.com"

    def __init__(self, access_token: str, project_id: str):
        "Initialize the ACC Client"
        try:
            self.access_token = access_token
            self.project_id = project_id
        except Exception as e:
            raise ValueError("Access token and project ID are required")
    
    def _url(self, path: str) -> str:
        "Generate a full URL for the given path"
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.BASE_URL}{path}"
    
    @property
    def headers(self) -> Dict[str, str]:
        "Generate headers for the given path"
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def get(self, path:str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        "Make a GET request to the given path"
        url = self._url(path)
        headers = self.headers
        r = requests.get(url, headers=headers, params=params)

        if r.status_code != 200:
            logger.error(f"GET failed with status code {r.status_code}")
            logger.error(r.text)
            raise Exception(f"GET failed with status code {r.status_code}")
        
        return r.json()

    def post(self, path:str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = self._url(path)
        headers = self.headers
        r = requests.post(url, headers=headers, json=body)

        if r.status_code != 200:
            logger.error(f"POST failed with status code {r.status_code}")
            logger.error(r.text)
            raise Exception(f"POST failed with status code {r.status_code}")
        
        return r.json()