# app_launcher.py
import sys
import os
import threading
import time
import webview

from bottle import run as bottle_run
from backend.main import app   # import your API app

# Detect if running as frozen exe
if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(sys.executable)
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIST = os.path.join(ROOT, "frontend", "dist", "index.html")


def start_backend():
    threading.Thread(
        target=lambda: bottle_run(app, host="localhost", port=8000),
        daemon=True
    ).start()


def run():
    start_backend()
    time.sleep(1)

    window = webview.create_window("CA Document Manager", FRONTEND_DIST)
    webview.start()


if __name__ == "__main__":
    run()
