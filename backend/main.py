from backend.api import API
from bottle import Bottle, run, request, response
from backend.cors import enable_cors

app = Bottle()
api = API()

@app.hook('after_request')
def add_cors_headers():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept"


@app.get("/greet/<name>")
def greet(name):
    return {"message": api.greet(name)}

@app.route("/<path:path>", method=["OPTIONS"])
def options_handler(path):
    return {}  # reply to OPTIONS preflight

@app.post("/api/login")
def login():
    try:
        response.content_type = "application/json"
        print("Entering Login Route")
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

def start_api():
    pass

if __name__ == "__main__":
    run(app, host="localhost", port=8000)