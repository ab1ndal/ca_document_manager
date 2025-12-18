# Source: ca_document_manager\platforms\acc\client.py
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging
import os
#import threading
#import time
#import webbrowser
#from http.server import HTTPServer, BaseHTTPRequestHandler
#from urllib.parse import urlparse, parse_qs, urlencode
import requests
from urllib.parse import urlencode
from backend import token_store

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()
"""
class OAuthHandler(BaseHTTPRequestHandler):
    code = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/callback":
            query = parse_qs(parsed.query)
            OAuthHandler.code = query.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth complete. You can close this tab.")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return
"""
@dataclass
class Client:
    BASE_URL: str = "https://developer.api.autodesk.com"

    def __init__(self):
        "Initialize the ACC Client"
        self.client_id = os.getenv("APS_CLIENT_ID")
        self.client_secret = os.getenv("APS_CLIENT_SECRET")
        #self.server = os.getenv("APS_SERVER", "localhost")
        #self.port = 9000
        self.redirect_uri = os.getenv("APS_REDIRECT_URI")
        self.project_id = os.getenv("ACC_PROJECT_ID")
        self.access_token = None
        self.user_id = None
        #self.project_id = project_id
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
    def build_auth_url(self) -> str:
        scopes = ["data:read"]
        auth_url = self._url("authentication/v2/authorize")
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
        }
        return auth_url + "?" + urlencode(params)

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

    def login(self) -> Dict[str, str]:
        """Login to the ACC API"""
        if self._refresh_tokens():
            return {"status": "ok"} 
        return {"auth_url": self.build_auth_url()}

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

    def clear_tokens(self):
        self.access_token = None
        self.user_id = None
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
        except Exception:
            pass

    