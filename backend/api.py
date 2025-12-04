from backend.platforms.acc.client import Client
from backend.platforms.acc.rfis import search_rfis
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import sys
import os

def load_env():
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller
        base_path = sys._MEIPASS    # internal temp folder
    else:
        # Running normally
        base_path = os.path.dirname(os.path.abspath(__file__))

    env_path = os.path.join(os.path.dirname(base_path), ".env")
    print("Loading ENV from:", env_path)
    load_dotenv(env_path)

load_env()

class API:
    def greet(self, name:str):
        return f"Hello {name}, from the python backend!"
        
    def __init__(self):
        self.client = Client()

    def login(self):
        try:
            self.client.login()
        except Exception as e:
            logger.error(f"[login] Login failed with error: {e}")
            raise
        return {"status": "ok"}

    def get_rfis(self, search_text=None, activity_after=None, limit=100, offset=0):
        PT = ZoneInfo("America/Los_Angeles")
        UTC = ZoneInfo("UTC")
        if activity_after:
            # Parse user input as Pacific Time
            # Expecting: yyyy-mm-ddTHH:MM
            dt_local = datetime.fromisoformat(activity_after)
            dt_local = dt_local.replace(tzinfo=PT)

            # Convert to UTC ISO8601 string (ACC requires UTC)
            dt_utc = dt_local.astimezone(UTC)
            after_iso = dt_utc.isoformat(timespec="seconds")

            # 1. Search by createdAt >= PT time (converted to UTC)
            created_results = search_rfis(
                self.client,
                search_text=search_text,
                created_after=after_iso,
                updated_after=None,
                limit=limit,
                offset=offset
            )

            # 2. Search by updatedAt >= PT time (converted to UTC)
            updated_results = search_rfis(
                self.client,
                search_text=search_text,
                created_after=None,
                updated_after=after_iso,
                limit=limit,
                offset=offset
            )

            # Merge both by RFI ID
            combined = {r["id"]: r for r in (created_results + updated_results)}
            return list(combined.values())

        # No date provided → default search
        return search_rfis(
            self.client,
            search_text=search_text,
            created_after=None,
            updated_after=None,
            limit=limit,
            offset=offset
        )

    def get_rfi_url(self, rfi_id):
        return f"https://acc.autodesk.com/docs/rfi/{rfi_id}"

    def export_excel(self, rows, path):
        df = pd.DataFrame(rows)
        df.to_excel(path, index=False)
        return {"saved": path}
