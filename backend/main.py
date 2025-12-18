from backend.api import API
from bottle import Bottle, run, request, response, redirect
#from backend.cors import enable_cors
import re
import os
import uuid

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

@app.route("/<path:path>", method=["OPTIONS"])
def options_handler(path):
    return {}  # reply to OPTIONS preflight

@app.get("/api/login")
def login():
    session_id = str(uuid.uuid4())

    # Create empty session in Redis
    api.client.set_session(session_id)

    result = api.login(session_id)

    return redirect(result["auth_url"])

@app.get("/callback")
def callback():
    session_id = request.query.state
    if not session_id:
        response.status = 400
        return "Missing session"

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
    session_id = request.headers.get("X-Session-Id")
    if not session_id:
        return {"logged_in": False}

    api.client.set_session(session_id)
    tokens = api.client.load_tokens()

    return {"logged_in": bool(tokens)}

@app.post("/api/rfis")
def get_rfis():
    session_id = request.headers.get("X-Session-Id")
    if not session_id:
        response.status = 401
        return {"error": "Missing session"}

    api.client.set_session(session_id)

    filters = request.json or {}
    items = api.get_rfis(filters)
    return {"items": items}


if __name__ == "__main__":
    run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000))
    )