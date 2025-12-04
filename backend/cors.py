def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # Set CORS headers
        from bottle import response
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept"
        # If it's a preflight OPTIONS request, return immediately
        if bottle.request.method == "OPTIONS":
            return {}
        return fn(*args, **kwargs)
    return _enable_cors
