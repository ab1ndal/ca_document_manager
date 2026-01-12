# Source: ca_document_manager\platforms\acc\client.py
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging
import os
import requests
from urllib.parse import urlencode
from backend import token_store

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

@dataclass
class Client:
    BASE_URL: str = "https://developer.api.autodesk.com"

    def __init__(self):
        "Initialize the ACC Client"
        self.client_id = os.getenv("APS_CLIENT_ID")
        self.client_secret = os.getenv("APS_CLIENT_SECRET")
        self.redirect_uri = os.getenv("APS_REDIRECT_URI")
        self.project_id = os.getenv("ACC_PROJECT_ID")
        self.access_token = None
        self.user_id = None
        self.session_id = None
        if not self.client_id or not self.client_secret:
            raise ValueError("APS_CLIENT_ID and APS_CLIENT_SECRET are required")
        if not self.project_id:
            raise ValueError("ACC_PROJECT_ID is required")
        if not self.redirect_uri:
            raise ValueError("APS_REDIRECT_URI is required")


    #--------------------------------------------
    #               UTILITY HELPER
    #--------------------------------------------
    def _url(self, path: str) -> str:
        "Generate a full URL for the given path"
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.BASE_URL}{path}"

    def set_session(self, session_id: str):
        self.session_id = session_id

    def load_tokens(self):
        return token_store.get_tokens(self.session_id)

    def save_tokens(self, tokens):
        token_store.set_tokens(self.session_id, tokens)
        self.access_token = tokens["access_token"]

    def clear_tokens(self):
        token_store.clear_tokens(self.session_id)
        self.access_token = None
        self.user_id = None

    #--------------------------------------------------
    #            OAUTH FLOW
    #--------------------------------------------------
    def build_auth_url(self, state: str) -> str:
        scopes = ["data:read"]
        auth_url = self._url("authentication/v2/authorize")
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        return auth_url + "?" + urlencode(params)

    def login_with_state(self, session_id: str):
        if self._refresh_tokens():
            return {"status": "ok"}
        return {
            "auth_url": self.build_auth_url(state=session_id)
        }

    def _refresh_tokens(self):
        "Refresh tokens"
        #print("Checking refresh tokens")
        stored = self.load_tokens()
        if not stored or "refresh_token" not in stored:
            #print("No refresh token found")
            return False
        url = self._url("authentication/v2/token")
        body = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": stored["refresh_token"]
        }
        new_tokens = requests.post(url, data=body)
        new_tokens.raise_for_status()
        if new_tokens.status_code != 200:
            #print("Refresh failed:", new_tokens.text)
            return False
        if new_tokens:
            self.save_tokens(new_tokens.json())
            self.access_token = new_tokens.json()["access_token"]
            return True
        return False

    def _get_tokens(self, code: str):
        "Get tokens from the given code"
        url = self._url("authentication/v2/token")
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        r = requests.post(url, data=data)
        r.raise_for_status()
        tokens = r.json()
        self.save_tokens(tokens)
        self.access_token = tokens["access_token"]

    def handle_callback(self, code: str):
        self._get_tokens(code)

    #----------------------------------------------------
    #             ACC API helpers
    #----------------------------------------------------
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
        if params:
            r = requests.get(url, headers=headers, params=params)
        else:
            r = requests.get(url, headers=headers)

        if r.status_code != 200:
            logger.error(f"GET failed with status code {r.status_code}L {r.text}")
            raise Exception(f"GET failed with status code {r.status_code}")
        
        return r.json()

    def post(self, path:str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        r = requests.post(self._url(path), headers=self.headers, json=body)
        if r.status_code != 200:
            logger.error(f"POST failed with status code {r.status_code}: {r.text}")
            raise Exception(f"POST failed with status code {r.status_code}")
        return r.json()

    def search_rfis(self, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url_path = f"construction/rfis/v3/projects/{self.project_id}/search:rfis"
        try:
            response = self.post(path=url_path, body=body)
        except Exception as e:
            logger.error(f"[Client] Search RFIs failed with error: {e}")
            raise
        return response

    def get_user_id(self) -> Optional[str]:
        path = f"construction/rfis/v3/projects/{self.project_id}/users/me"
        try:
            response = self.get(path=path)
        except Exception as e:
            logger.error(f"[Client] Get user ID failed with error: {e}")
            raise
        return response["user"]["id"]

    def get_rfi_types(self) -> Optional[List[Dict[str, Any]]]:
        path = f"construction/rfis/v3/projects/{self.project_id}/rfi-types"
        try:
            response = self.get(path=path)
        except Exception as e:
            logger.error(f"[Client] Get RFI types failed with error: {e}")
            raise
        return response

    def get_rfi_attributes(self):
        path = f"construction/rfis/v3/projects/{self.project_id}/attributes"
        print("In the Get Attribute Pathway")
        try:
            res = self.get(path=path)
            print("Response:", res)
            return res
        except Exception as e:
            if "status code 403" not in str(e):
                raise
            logger.warning("RFI attributes endpoint blocked; falling back to search-based attributes.")
            return self._get_rfi_attributes_via_search()

    def _get_rfi_attributes_via_search(self, limit: int = 2):
        body = {
            "limit": limit,
            "offset": 0,
            "fields": ["customAttributes"],
        }
        try:
            response = self.search_rfis(body=body)
        except Exception as e:
            logger.error(f"[Client] Search fallback for attributes failed: {e}")
            raise
        results = response.get("results", [])
        return self._extract_custom_attributes(results)

    def _extract_custom_attributes(self, results):
        attributes = {}
        for rfi in results:
            raw = rfi.get("customAttributes") or rfi.get("customAttributeValues")
            print(raw)
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict):
                        attr_id = (
                            item.get("id")
                            or item.get("attributeId")
                            or item.get("definitionId")
                            or item.get("name")
                            or item.get("displayName")
                        )
                        if not attr_id:
                            continue
                        attr_name = (
                            item.get("name")
                            or item.get("displayName")
                            or item.get("label")
                            or item.get("title")
                            or attr_id
                        )
                        attributes[attr_id] = attr_name
                    elif isinstance(item, str):
                        attributes[item] = item
            elif isinstance(raw, dict):
                for key in raw.keys():
                    attributes[key] = key
        return [{"id": attr_id, "name": name} for attr_id, name in sorted(attributes.items(), key=lambda x: x[1])]
