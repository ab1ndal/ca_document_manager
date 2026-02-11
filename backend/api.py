from backend.platforms.acc.client import Client
from backend.platforms.acc.rfis import search_rfis
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import sys
import os
import logging
import json
from backend import token_store

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

    def login(self, session_id: str):
        try:
            return self.client.login_with_state(session_id)
        except Exception as e:
            logger.error(f"[login] Login failed with error: {e}")
            raise

    def get_rfis(self, filters):
        search_text = filters.get("searchText", " ")
        activity_after = filters.get("updatedAfter", None)
        limit = filters.get("limit", 200)
        
        if not self.client.user_id:
            self.client.user_id = [self.client.get_user_id()]

        if activity_after:
            # 1. Search by createdAt >= PT time (converted to UTC)
            created_ids = search_rfis(
                self.client,
                search_text=search_text,
                created_after=activity_after,
                updated_after=None,
                limit=limit
            )

            # 2. Search by updatedAt >= PT time (converted to UTC)
            updated_ids = search_rfis(
                self.client,
                search_text=search_text,
                created_after=None,
                updated_after=activity_after,
                limit=limit
            )
            # Merge both by RFI ID
            search_ids = list(set(created_ids) | set(updated_ids))
            
        else:
            # No date provided → default search
            search_ids = search_rfis(
                self.client,
                search_text=search_text,
                created_after=None,
                updated_after=None,
                limit=limit
            )
        print("Search IDs:", search_ids)
        return search_ids


    def get_rfi_attributes(self):
        try:
            attributes = self.client.get_rfi_attributes()
            return attributes
        except Exception as e:
            logger.error(f"[get_rfi_attributes] Failed: {e}")
            raise

    def get_increment_configs(self):
        """Get all increment configurations"""
        try:
            config_key = f"increments"
            stored = token_store.get_config(config_key)
            
            if stored:
                try:
                    return json.loads(stored)
                except json.JSONDecodeError:
                    return {"configs": {}}
            return {"configs": {}}
        except Exception as e:
            logger.error(f"[get_increment_configs] Failed: {e}")
            return {"configs": {}}

    def get_increment_config(self, increment):
        """Get configuration for a specific increment"""
        try:
            all_configs = self.get_increment_configs()
            print("Getting increment config:", all_configs)
            return all_configs.get("configs", {}).get(increment, None)
        except Exception as e:
            logger.error(f"[get_increment_config] Failed: {e}")
            return None

    def save_increment_configs(self, configs):
        """Save all increment configurations"""
        try:
            config_key = f"increments"
            print("Saving increment configs:", configs)
            token_store.set_config(config_key, json.dumps(configs))
            return {"status": "success"}
        except Exception as e:
            logger.error(f"[save_increment_configs] Failed: {e}")
            raise

    def get_field_config(self):
        try:
            config_key = f"config:fields:{self.client.session_id}"
            stored = token_store.get_config(config_key)
        except Exception as e:
            logger.error(f"[get_field_config] Failed: {e}")
            return {"fields": []}
        if stored:
            try:
                return json.loads(stored)
            except json.JSONDecodeError:
                return {"fields": []}
        return {"fields": []}

    def save_field_config(self, config):
        try:
            config_key = f"config:fields:{self.client.session_id}"
            token_store.set_config(config_key, json.dumps(config))
        except Exception as e:
            logger.error(f"[save_field_config] Failed: {e}")
            raise

    def get_rfi_url(self, rfi_id):
        return f"https://acc.autodesk.com/docs/rfi/{rfi_id}"

    def export_excel(self, rows, path):
        df = pd.DataFrame(rows)
        df.to_excel(path, index=False)
        return {"saved": path}
