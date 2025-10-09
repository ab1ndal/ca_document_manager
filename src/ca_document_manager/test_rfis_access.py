import os
import json
import threading
import webbrowser
import time
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.getenv("APS_CLIENT_ID")
CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET")
REDIRECT_URI = os.getenv("APS_REDIRECT_URI", "http://127.0.0.1:9000/callback")
PROJECT_ID = os.getenv("ACC_PROJECT_ID")  # e.g. b473ef72-b524-429c-bb7e-a657af7433ea


# ---------------------------
# Local server to capture callback
# ---------------------------
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


def start_server():
    server = HTTPServer(("127.0.0.1", 9000), OAuthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


# ---------------------------
# OAuth helpers
# ---------------------------
def get_tokens(code: str):
    url = "https://developer.api.autodesk.com/authentication/v2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()


# ---------------------------
# RFI API calls
# ---------------------------
def get_rfi_user_me(token):
    """Check if the current user is recognized in the RFIs system"""
    url = "https://developer.api.autodesk.com/acc/v1/rfis/v1/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    print("\n[RFI User Me] raw response:", r.status_code)
    print(r.text[:500])
    if r.status_code == 200:
        print("\nParsed JSON:")
        print(json.dumps(r.json(), indent=2))


def search_rfis(token, project_id, limit=5):
    """Search RFIs via POST"""
    url = "https://developer.api.autodesk.com/acc/v1/rfis/v2/rfis:search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "filter": {
            "projectId": project_id
        },
        "page": {
            "limit": limit
        }
    }
    r = requests.post(url, headers=headers, json=body)
    print("\n[Search RFIs] raw response:", r.status_code)
    print(r.text[:500])
    if r.status_code == 200:
        print("\nParsed JSON:")
        print(json.dumps(r.json(), indent=2))


# ---------------------------
# Main flow
# ---------------------------
def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Set APS_CLIENT_ID and APS_CLIENT_SECRET in your .env file")
        return
    if not PROJECT_ID:
        print("Set ACC_PROJECT_ID in your .env file")
        return

    scopes = ["data:read"]  # minimal for RFIs read
    auth_url = "https://developer.api.autodesk.com/authentication/v2/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(scopes),
    }
    url = auth_url + "?" + urlencode(params)

    server = start_server()
    print("Opening browser for login...")
    webbrowser.open(url)

    for _ in range(60):
        if OAuthHandler.code:
            break
        time.sleep(1)
    server.shutdown()

    if not OAuthHandler.code:
        print("No auth code received")
        return

    tokens = get_tokens(OAuthHandler.code)
    access_token = tokens["access_token"]
    print("\nGot access token.")

    # Step 1: Check if user is recognized in RFIs API
    get_rfi_user_me(access_token)

    # Step 2: Try searching RFIs in the project
    print(f"\nUsing project ID: {PROJECT_ID}")
    search_rfis(access_token, PROJECT_ID)


if __name__ == "__main__":
    main()
