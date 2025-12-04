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

def start_api():
    pass

if __name__ == "__main__":
    run(app, host="localhost", port=8000)