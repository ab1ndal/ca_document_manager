import webview
from backend.api import API

def start():
    api = API()

    window = webview.create_window(
        title="CA Manager",
        url="http://localhost:5173",
        js_api=api,
        width=1300,
        height=900,
    )

    webview.start(debug=True)

if __name__ == "__main__":
    start()
