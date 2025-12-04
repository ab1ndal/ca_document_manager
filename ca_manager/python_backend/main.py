from ca_document_manager.platforms.acc.client import Client
from ca_document_manager.platforms.acc.rfis import search_rfis
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

client = Client()

def login():
    client.login()
    return {"status": "ok"}

def get_rfis(search_text=None, activity_after=None, limit=100, offset=0):
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
            client,
            search_text=search_text,
            created_after=after_iso,
            updated_after=None,
            limit=limit,
            offset=offset
        )

        # 2. Search by updatedAt >= PT time (converted to UTC)
        updated_results = search_rfis(
            client,
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
        client,
        search_text=search_text,
        created_after=None,
        updated_after=None,
        limit=limit,
        offset=offset
    )

def get_rfi_url(rfi_id):
    return f"https://acc.autodesk.com/docs/rfi/{rfi_id}"

def export_excel(rows, path):
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)
    return {"saved": path}
