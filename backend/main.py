from backend.api import API
from bottle import Bottle, run, request, response
from backend.cors import enable_cors
import re
import os

app = Bottle()
api = API()

@app.hook('after_request')
def add_cors_headers():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept"

@app.route("/<path:path>", method=["OPTIONS"])
def options_handler(path):
    return {}  # reply to OPTIONS preflight

@app.post("/api/login")
def login():
    try:
        response.content_type = "application/json"
        #print("Entering Login Route")
        result = api.login()
        return result
    except Exception as e:
        response.status = 500
        return {"error": str(e)}

@app.get("/api/auth/status")
def auth_status():
    response.content_type = "application/json"
    tokens = api.client._load_tokens()
    logged_in = bool(tokens and tokens.get("access_token"))
    return {"logged_in": logged_in}

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