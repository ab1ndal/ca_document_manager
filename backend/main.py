import webview
from api import API
import threading

def start():
    api = API()

    window = webview.create_window(
        title="CA Manager",
        url="http://localhost:5173",
        js_api=api,
        width=1300,
        height=900
    )

    webview.start(debug=True)

def start_api():
    pass

if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()
    start()
