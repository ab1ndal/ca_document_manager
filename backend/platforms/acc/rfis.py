# Source: ca_document_manager\platforms\acc\rfis.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.platforms.acc.client import Client
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

PST = ZoneInfo("America/Los_Angeles")
UTC = ZoneInfo("UTC")

def to_utc_iso(dt_str: str) -> str:
    # Parse PST local time (no timezone in string)
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
    # Attach PST timezone
    dt = dt.replace(tzinfo=PST)
    # Convert to UTC
    dt_utc = dt.astimezone(UTC)
    # Format as UTC ISO string
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

logger = logging.getLogger(__name__)

def create_date_range(start: Optional[datetime]=None, end: Optional[datetime]=None)->Optional[str]:
    if not start and not end:
        return None

    if start:
        start_date = to_utc_iso(start)
    else:
        start_date = ""
    if end:
        end_date = to_utc_iso(end)
    else:
        end_date = ""

    if start and end:
        return f"{start_date}..{end_date}"
    elif start:
        return f"{start_date}..9999-12-31T23:59:59Z"
    elif end:
        return f"..{end_date}"

def search_rfis(
    client: Client, 
    *,
    search_text: Optional[str] = None,
    created_after: Optional[datetime]=None,
    updated_after: Optional[datetime]=None,
    limit: int = 200
) -> List[str]:
    offset = 0

    # Create filters
    filters = {
        "status": ["open", "openRev1", "openRev2"],
        "assignedTo": client.user_id
    }

    if created_after:
        filters["createdAt"] = create_date_range(start=created_after)

    if updated_after:
        filters["updatedAt"] = create_date_range(start=updated_after)


    body = {
        "limit": limit,
        "offset": offset,
        "search": search_text,
        "sort":[{
            "field": "createdAt",
            "order": "ASC"
        }],
        "filter": filters,
        "fields": ["id"]
    }

    try:
        response = client.search_rfis(body=body)
    except Exception as e:
        logger.error(f"[search_rfis] Search RFIs failed with error: {e}")
        raise

    ids = []

    for r in response.get("results", []):
        ids.append(r.get("id"))

    return ids