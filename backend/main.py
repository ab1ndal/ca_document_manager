from backend.api import API
from bottle import Bottle, run, request, response
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
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept"

@app.route("/<path:path>", method=["OPTIONS"])
def options_handler(path):
    return {}  # reply to OPTIONS preflight

@app.post("/api/login")
def login():
    session_id = request.get_cookie("session_id")

    IS_PROD = os.getenv("ENV") == "PROD"

    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            "session_id",
            session_id,
            httponly=True,
            secure=IS_PROD,
            samesite="None" if IS_PROD else "Lax"
        )

    api.client.set_session(session_id)
    return api.login()

@app.get("/callback")
def callback():
    session_id = request.get_cookie("session_id")
    if not session_id:
        response.status = 400
        return "Missing session"

    api.client.set_session(session_id)
    api.client.handle_callback(request.query.code)

    return bottle.redirect(os.getenv("FRONTEND_URL"))

@app.post("/api/logout")
def logout():
    session_id = request.get_cookie("session_id")
    if session_id:
        api.client.set_session(session_id)
        api.client.clear_tokens()

    response.delete_cookie("session_id")
    return {"status": "logged_out"}

@app.get("/api/auth/status")
def auth_status():
    session_id = request.get_cookie("session_id")
    if not session_id:
        return {"logged_in": False}

    api.client.set_session(session_id)
    tokens = api.client.load_tokens()
    return {"logged_in": bool(tokens)}

@app.post("/api/rfis")
def get_rfis():
    response.content_type = "application/json"
    try:
        filters = request.json or {}
        #print("Incomming Filters in main:", filters)
        items = api.get_rfis(filters)
        #print(f"returned {len(items)} RFIs")
        return {"items": items}
    except Exception as e:
        error_str = str(e)
        match = re.search(r"status code (\d+)", error_str)
        if match:
            status_code = int(match.group(1))
            response.status = status_code
            #print(f"API Error ({status_code}): {error_str}")
            return {"error": error_str}
        import traceback
        print("\n=== ERROR in /api/rfis ===")
        traceback.print_exc()
        response.status = 500
        return {"error": str(e)}


if __name__ == "__main__":
    run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000))
    )