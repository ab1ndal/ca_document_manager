from backend.platforms.acc.client import Client
from backend.platforms.acc.rfis import search_rfis
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import sys
import os
import logging

logger = logging.getLogger(__name__)

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
            print("Trying Client Login")
            self.client.login()
        except Exception as e:
            logger.error(f"[login] Login failed with error: {e}")
            raise
        return {"status": "ok"}

    def get_rfis(self, filters):
        search_text = filters.get("searchText", None)
        activity_after = filters.get("updatedAfter", None)
        limit = filters.get("limit", 100)

        print("Entered innermost layers", filters)

        
        PT = ZoneInfo("America/Los_Angeles")
        UTC = ZoneInfo("UTC")
        if activity_after:
            print("activity_after", activity_after)
            print("Type of activity_after", type(activity_after))
            # Parse user input as Pacific Time
            # Expecting: yyyy-mm-ddTHH:MM
            #dt_local = datetime.fromisoformat(activity_after)
            #dt_local = dt_local.replace(tzinfo=PT)

            # Convert to UTC ISO8601 string (ACC requires UTC)
            #dt_utc = dt_local.astimezone(UTC)
            #after_iso = dt_utc.isoformat(timespec="seconds")

            # 1. Search by createdAt >= PT time (converted to UTC)
            print("Searching the RFIs Part 1")
            created_results = search_rfis(
                self.client,
                search_text=search_text,
                created_after=activity_after,
                updated_after=None,
                limit=limit
            )

            print(created_results)

            # 2. Search by updatedAt >= PT time (converted to UTC)
            print("Searching the RFIs Part 2")
            updated_results = search_rfis(
                self.client,
                search_text=search_text,
                created_after=None,
                updated_after=activity_after,
                limit=limit
            )

            print(updated_results)

            # Merge both by RFI ID
            combined = {r["id"]: r for r in (created_results + updated_results)}
            print(combined)
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
