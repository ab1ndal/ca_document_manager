from backend.api import API
from bottle import Bottle, run, request, response, redirect
#from backend.cors import enable_cors
import json
import os
import uuid
import re
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

app = Bottle()
api = API()

@app.hook('after_request')
def add_cors_headers():
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept, X-Session-Id"
    response.headers["Access-Control-Allow-Credentials"] = "true"

@app.error(500)
def error500(error):
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept, X-Session-Id"
    return {"error": str(error.exception)}

@app.route("/<path:path>", method=["OPTIONS"])
def options_handler(path):
    return {}  # reply to OPTIONS preflight

@app.get("/api/login")
def login():
    session_id = "global"
    # Create empty session in Redis
    api.client.set_session(session_id)
    result = api.login(session_id)
    if result.get("status") == "ok":
        return redirect(f"{os.getenv('FRONTEND_URL')}?session_id={session_id}")
    return redirect(result["auth_url"])

@app.get("/callback")
def callback():
    session_id = "global"
    api.client.set_session(session_id)
    api.client.handle_callback(request.query.code)
    return redirect(f"{os.getenv('FRONTEND_URL')}?session_id={session_id}")

@app.post("/api/logout")
def logout():
    session_id = request.headers.get("X-Session-Id")
    if session_id:
        api.client.set_session(session_id)
        api.client.clear_tokens()
    return {"status": "logged_out"}

@app.get("/api/auth/status")
def auth_status():
    session_id = request.headers.get("X-Session-Id") or "global"
    api.client.set_session(session_id)
    tokens = api.client.load_tokens()
    return {"logged_in": bool(tokens)}

def get_custom_mapping():
    field_list_path = Path(__file__).parent / "userInput" / "fieldList.json"
    with open(field_list_path, "r") as f:
        field_list = json.load(f)
    return field_list["custom_groups"]


def flatten_custom_attributes(rfi: dict) -> dict:
    custom_attrs = rfi.pop("customAttributes", [])

    for attr in custom_attrs:
        attr_id = attr.get("id")
        values = attr.get("values", [])
        if attr_id and values:
            if attr_id in get_custom_mapping():
                rfi[attr_id] = get_custom_mapping()[attr_id]["options"][values[0]]
            else:
                rfi[attr_id] = values[0]
    return rfi

@app.post("/api/rfis")
def get_rfis():
    session_id = request.headers.get("X-Session-Id") or "global"
    api.client.set_session(session_id)

    filters = request.json or {}
    items = api.get_rfis(filters)
    desired_fields = filters.get("fields", None)

    full = []
    for rfi_id in items:
        try:
            full.append(flatten_custom_attributes(api.client.get_rfi_by_id(rfi_id)))
        except Exception as e:
            continue
    def pick_fields(obj: dict, desired: list[str]) -> dict:
        out = {}
        for key in desired:
            out[key] = obj.get(key)
        return out
    
    desired_fields = desired_fields or ["id", "customIdentifier", "title", "status"]
    rows = [pick_fields(rfi, desired_fields) for rfi in full]
    results = {r["customIdentifier"]: r for r in rows}
    return {"items": rows}

@app.get("/api/rfis/attributes")
def get_rfi_attributes():
    session_id = request.headers.get("X-Session-Id") or "global"
    api.client.set_session(session_id)
    attributes = api.get_rfi_attributes()
    return {"attributes": attributes}

@app.get("/api/config/fields")
def get_field_config():
    session_id = request.headers.get("X-Session-Id") or "global"
    api.client.set_session(session_id)
    try:
        config = api.get_field_config()
    except Exception as e:
        logger.error(f"[get_field_config] Failed: {e}")
        return {"fields": []}
    return config

@app.post("/api/config/fields")
def save_field_config():
    session_id = request.headers.get("X-Session-Id") or "global"
    api.client.set_session(session_id)
    config = request.json or {}
    try:
        api.save_field_config(config)
    except Exception as e:
        logger.error(f"[save_field_config] Failed: {e}")
        return {"status": "failed"}
    return {"status": "saved"}

@app.get("/api/config/increments")
def get_increment_configs():
    """
    Get all saved increment configurations
    Returns: { "configs": { "INC 1": {...}, "INC 2": {...}, ... } }
    """
    session_id = request.headers.get("X-Session-Id") or "global"
    api.client.set_session(session_id)
    try:
        configs = api.get_increment_configs()
        return configs
    except Exception as e:
        logger.error(f"Failed to get increment configs: {e}")
        return {"error": str(e)}, 500

@app.post("/api/config/increments")
def save_increment_configs():
    """
    Save all increment configurations
    Body: { "configs": { "INC 1": { "searchTerm": "", "fields": [...] }, ... } }
    """
    session_id = request.headers.get("X-Session-Id") or "global"
    api.client.set_session(session_id)
    body = request.json or {}
    try:
        configs = body.get("configs", {})
        result = api.save_increment_configs(configs)
        return result
    except Exception as e:
        logger.error(f"Failed to save increment configs: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000))
    )