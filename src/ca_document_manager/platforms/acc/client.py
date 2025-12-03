# Source: src\ca_document_manager\platforms\acc\client.py
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging
import os
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
import requests

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

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

@dataclass
class Client:
    BASE_URL: str = "https://developer.api.autodesk.com"

    def __init__(self):
        "Initialize the ACC Client"
        self.client_id = os.getenv("APS_CLIENT_ID")
        self.client_secret = os.getenv("APS_CLIENT_SECRET")
        self.server = os.getenv("APS_SERVER", "127.0.0.1")
        self.port = os.getenv("APS_PORT", 9000)
        self.redirect_uri = f"http://{self.server}:{self.port}/callback"
        self.project_id = os.getenv("ACC_PROJECT_ID")
        self.token_file = os.getenv("APS_TOKEN_FILE", "aps_token.json")
        self.access_token = None
        #self.project_id = project_id
        if not self.client_id or not self.client_secret:
            raise ValueError("APS_CLIENT_ID and APS_CLIENT_SECRET are required")
        if not self.project_id:
            raise ValueError("ACC_PROJECT_ID is required")

    def _url(self, path: str) -> str:
        "Generate a full URL for the given path"
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.BASE_URL}{path}"

    def _load_tokens(self):
        "Load tokens from file"
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _save_tokens(self, tokens: Dict[str, Any]):
        "Save tokens to file"
        with open(self.token_file, "w") as f:
            json.dump(tokens, f)

    def _refresh_tokens(self):
        "Refresh tokens"
        stored = self._load_tokens()
        if not stored or "refresh_token" not in stored:
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
            print("Refresh failed:", new_tokens.text)
            return False
        if new_tokens:
            self._save_tokens(new_tokens.json())
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
        return r.json()

    def login(self):
        if not self._refresh_tokens():
            server = HTTPServer((self.server, self.port), OAuthHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            scopes = ["data:read"]
            auth_url = self._url("authentication/v2/authorize")
            params = {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "scope": " ".join(scopes),
            }
            url = auth_url + "?" + urlencode(params)
            webbrowser.open(url)

            for _ in range(60):
                if OAuthHandler.code:
                    break
                time.sleep(1)
            server.shutdown()

            if not OAuthHandler.code:
                raise Exception("No auth code received") 

            tokens = self._get_tokens(OAuthHandler.code)
            self._save_tokens(tokens)
            self.access_token = tokens["access_token"]

        return self.access_token

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
