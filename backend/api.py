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

    env_path = os.path.join(base_path, ".env")
    #print("Loading ENV from:", env_path)
    load_dotenv(env_path)

load_env()

class API:
        
    def __init__(self):
        self.client = Client()

    def login(self):
        try:
            return self.client.login()
        except Exception as e:
            logger.error(f"[login] Login failed with error: {e}")
            raise

    def get_rfis(self, filters):
        search_text = filters.get("searchText", None)
        activity_after = filters.get("updatedAfter", None)
        limit = filters.get("limit", 100)
        
        #print("Inside API call")
        if not self.client.user_id:
            self.client.user_id = [self.client.get_user_id()]

        if activity_after:
            # 1. Search by createdAt >= PT time (converted to UTC)
            #print("Searching via creation date")
            created_results = search_rfis(
                self.client,
                search_text=search_text,
                created_after=activity_after,
                updated_after=None,
                limit=limit
            )

            # 2. Search by updatedAt >= PT time (converted to UTC)
            #print("Searching via Update date")
            updated_results = search_rfis(
                self.client,
                search_text=search_text,
                created_after=None,
                updated_after=activity_after,
                limit=limit
            )

            # Merge both by RFI ID
            combined = {r["customIdentifier"]: r for r in (created_results + updated_results)}
            #print(combined)
            return list(combined.values())

        # No date provided → default search
        return search_rfis(
            self.client,
            search_text=search_text,
            created_after=None,
            updated_after=None,
            limit=limit
        )

    def get_rfi_url(self, rfi_id):
        return f"https://acc.autodesk.com/docs/rfi/{rfi_id}"

    def export_excel(self, rows, path):
        df = pd.DataFrame(rows)
        df.to_excel(path, index=False)
        return {"saved": path}
