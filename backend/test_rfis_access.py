import os
import json
import threading
import webbrowser
import time
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import base64

# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.getenv("APS_CLIENT_ID")
CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET")
REDIRECT_URI = os.getenv("APS_REDIRECT_URI", "http://localhost:8000/callback")
PROJECT_ID = os.getenv("ACC_PROJECT_ID")
TOKEN_FILE = os.getenv("APS_TOKEN_FILE", "aps_token.json")


# ---------------------------
# Local server to capture callback
# ---------------------------

def print_token_scopes(access_token: str):
    try:
        parts = access_token.split(".")
        if len(parts) < 2:
            print("Token is not JWT formatted")
            return
        payload_b64 = parts[1] + "==="
        payload_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        payload = json.loads(payload_json)
        print("Token scopes:", payload.get("scope") or payload.get("scp"))
    except Exception as e:
        print("Could not decode token payload:", e)

def save_pretty_json(data: dict, prefix: str, folder: str = "outputs"):
    Path(folder).mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = Path(folder) / f"{prefix}_{ts}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved JSON to: {file_path.resolve()}")

def load_tokens():
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

def refresh_tokens(refresh_token):
    url = "https://developer.api.autodesk.com/authentication/v2/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print("[!] Refresh failed:", r.text)
        return None
    return r.json()

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
    server = HTTPServer(("localhost", 8000), OAuthHandler)
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
def get_rfi_user_me(token, project_id):
    """Check if the current user is recognized in the RFIs system"""
    print("Auth token:", token)
    url = f"https://developer.api.autodesk.com/construction/rfis/v3/projects/{project_id}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    print("\n[RFI User Me] raw response:", r.status_code)
    print(r.text[:500])
    if r.status_code == 200:
        data = r.json()
        save_pretty_json(data, "rfis_user_me")

def get_all_users(token, project_id):
    """Check if the current user is recognized in the RFIs system"""
    print("Auth token:", token)
    url = f"https://developer.api.autodesk.com/construction/admin/v1/projects/{project_id}/users"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    print("\n[RFI User Me] raw response:", r.status_code)
    print(r.text[:500])
    if r.status_code == 200:
        data = r.json()
        save_pretty_json(data, "all_users")


def search_rfis(token, project_id, limit=5):
    """Search RFIs via POST"""
    url = f"https://developer.api.autodesk.com/construction/rfis/v3/projects/{project_id}/search:rfis"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "limit": limit,
        "offset": 0,
    }
    r = requests.post(url, headers=headers, json=body)
    print("\n[Search RFIs] raw response:", r.status_code)
    print(r.text[:500])
    if r.status_code == 200:
        data = r.json()
        save_pretty_json(data, "rfis_search")

def get_rfi_by_id(token, project_id, rfi_id):
    url = f"https://developer.api.autodesk.com/construction/rfis/v3/projects/{project_id}/rfis/{rfi_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(url, headers=headers)
    print("Status:", r.status_code)
    if not r.status_code == 200:
        print(r.text[:200])
        return
    else:
        data = r.json()
        save_pretty_json(data, "rfis_by_id")
        return r.json()

def get_custom_attributes(token, project_id):
    url = f"https://developer.api.autodesk.com/construction/rfis/v3/projects/{project_id}/attributes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    r = requests.get(url, headers=headers)
    print("[Get RFI Attributes] Status:", r.status_code)
    # Helpful debug headers
    req_id = r.headers.get("x-request-id") or r.headers.get("x-ads-request-id")
    if req_id:
        print("Request ID:", req_id)

    print("WWW-Authenticate:", r.headers.get("www-authenticate"))
    print("Content-Type:", r.headers.get("content-type"))

    if r.status_code != 200:
        print("Body:", r.text[:500])
        return None

    data = r.json()
    save_pretty_json(data, "rfis_attributes")
    return data

def find_rfi_by_custom_identifier(token, project_id, identifier):
    url = f"https://developer.api.autodesk.com/construction/rfis/v3/projects/{project_id}/search:rfis"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "search": identifier,
        "limit": 200
    }

    r = requests.post(url, headers=headers, json=body)
    print("Status:", r.status_code)
    if not r.status_code == 200:
        print(r.text[:200])
        return
    if r.status_code == 200:
        data = r.json()
        #save_pretty_json(data, "rfis_by_custom_id")
    return data["results"][0]["id"]

def get_rfis_with_attachments(project_id, token, limit=100):
    url = f"https://developer.api.autodesk.com/construction/rfis/v3/projects/{project_id}/search:rfis"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    offset = 0
    collected = []

    while True:
        payload = {
            "limit": limit,
            "offset": offset,
            "fields": [
                "id",
                "customIdentifier",
                "title",
                "attachmentsCount"
            ]
        }

        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            print(resp.text)
            break

        data = resp.json()
        results = data.get("results", [])

        # Filter only RFIs with attachmentsCount > 0
        for r in results:
            if r.get("attachmentsCount", 0) > 0:
                collected.append({
                    "id": r["id"],
                    "number": r.get("customIdentifier"),
                    "title": r.get("title"),
                    "attachmentsCount": r.get("attachmentsCount"),
                })

        # Pagination
        pag = data.get("pagination", {})
        total = pag.get("totalResults", 0)
        offset += limit

        if offset >= total:
            break

    return collected

def get_rfi_attachments(token, project_id, rfi_id):
    """
    Returns list of attachments (files and document references) for a given RFI.
    """

    url = f"https://developer.api.autodesk.com/construction/rfis/v3/projects/{project_id}/rfis/{rfi_id}/attachments"
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("Error fetching attachments:", r.text)
        return []

    data = r.json()
    print("Getting RFIs was a success")
    print(data)
    return data.get("results", [])

def download_from_storage_urn(token, storage_urn, display_name, local_path):
    """
    Generates a signed S3 download URL and downloads the file.
    """

    prefix = "urn:adsk.objects:os.object:"
    if not storage_urn.startswith(prefix):
        print("Invalid storage URN:", storage_urn)
        return False

    # Extract bucket and object id
    clean = storage_urn[len(prefix):]        # wip.dm.prod/xxxxxx.pdf
    bucket, object_id = clean.split("/", 1)  # bucket = wip.dm.prod, object_id = xxx.pdf

    # Step 1: Request signed S3 download link
    signed_url_endpoint = f"https://developer.api.autodesk.com/oss/v2/buckets/{bucket}/objects/{object_id}/signeds3download"
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(signed_url_endpoint, headers=headers)
    if r.status_code != 200:
        print("Failed to get signed URL:", r.text)
        return False

    signed_data = r.json()
    signed_url = signed_data.get("url")

    if not signed_url:
        print("No signed URL found in response")
        return False

    # Step 2: Now download using the signed URL (no auth required)
    r = requests.get(signed_url, stream=True)
    if r.status_code != 200:
        print("Download failed:", r.text)
        return False

    with open(local_path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)

    print(f"Saved: {local_path}")
    return True


def download_file(url, local_path):
    print("Downloading file")
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        print("Download failed:", r.status_code)
        return False

    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Downloaded file")
    return True

def download_rfi_attachments(token, project_id, rfi_json, base_folder="downloads"):
    """
    For a given RFI JSON block, download all attachments into a local folder.
    """

    rfi_id = rfi_json["id"]
    rfi_number = rfi_json.get("customIdentifier", rfi_id)

    # Create folder for this RFI
    rfi_folder = os.path.join(base_folder, rfi_number)
    os.makedirs(rfi_folder, exist_ok=True)

    attachments = get_rfi_attachments(token, project_id, rfi_id)

    if not attachments:
        print(f"No attachments found for RFI {rfi_number}")
        return

    print("Found attachments")
    print(attachments)
    for att in attachments:
        display_name = att.get("displayName", att.get("fileName"))
        storage_urn = att.get("storageUrn")
        if not storage_urn:
            print(f"Skipping {display_name}: no storage URN")
            continue

        local_path = os.path.join(rfi_folder, display_name)
        success = download_from_storage_urn(token, storage_urn, display_name, local_path)

        if success:
            print(f"Saved: {local_path}")
        else:
            print(f"Failed: {display_name}")

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

    scopes = ["data:read", "account:read"]  # minimal for RFIs read
    auth_url = "https://developer.api.autodesk.com/authentication/v2/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(scopes),
    }
    url = auth_url + "?" + urlencode(params)

    # ---------------------------------------
    # 1. Try loading existing refresh token
    # ---------------------------------------
    stored = load_tokens()

    if stored and "refresh_token" in stored:
        print("Using stored refresh token...")
        new_tokens = refresh_tokens(stored["refresh_token"])
        if new_tokens:
            print("Token refreshed successfully.")
            save_tokens(new_tokens)
            access_token = new_tokens["access_token"]
        else:
            print("Stored refresh token invalid. Running full OAuth login.")
            stored = None

    # ---------------------------------------
    # 2. Run full OAuth login if needed
    # ---------------------------------------
    if not stored:
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
        save_tokens(tokens)
        access_token = tokens["access_token"]
        print("\nGot access token.")

    # Step 1: Check if user is recognized in RFIs API
    get_rfi_user_me(access_token, PROJECT_ID)
    get_all_users(access_token, PROJECT_ID)

    # Print token scopes
    #print_token_scopes(access_token)

    # Step 2: Try searching RFIs in the project
    #print(f"\nUsing project ID: {PROJECT_ID}")
    #search_rfis(access_token, PROJECT_ID)

    # Step 3: Try getting a specific RFI
    #rfi_id = "9aa5b442-f532-4e1c-98c1-34b4c83ef246"
    #get_rfi_by_id(access_token, PROJECT_ID, rfi_id)

    # Step 4: Try finding an RFI by custom identifier
    #identifier = "Test RFI"
    #rfi_id = find_rfi_by_custom_identifier(access_token, PROJECT_ID, identifier)
    #get_rfi_by_id(access_token, PROJECT_ID, rfi_id)

    # Step 5: Try getting RFIs with attachments
    #rfis = get_rfis_with_attachments(PROJECT_ID, access_token)
    #print("\nRFIs with attachments:")
    #for rfi in rfis:
    #    print(f"- {rfi['number']} | {rfi['title']} | {rfi['id']} (attachments: {rfi['attachmentsCount']})")

    # Step 6: Try downloading attachments for a specific RFI
    #identifier = "00127"
    #result = find_rfi_by_custom_identifier(access_token, PROJECT_ID, identifier)
    #if result and result.get("results"):
    #    rfi_json = result["results"][0]
    #    download_rfi_attachments(access_token, PROJECT_ID, rfi_json)

    # Step 7: List of custom attributes
    #get_custom_attributes(access_token, PROJECT_ID)


if __name__ == "__main__":
    main()
