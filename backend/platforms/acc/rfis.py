# Source: ca_document_manager\platforms\acc\rfis.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.platforms.acc.client import Client

def create_date_range(start: Optional[datetime]=None, end: Optional[datetime]=None)->Optional[str]:
    if not start and not end:
        return None
    start_date, end_date = "", ""
    if start:
        start_date = f"{start.isoformat()}Z"
    if end:
        end_date = f"{end.isoformat()}Z"
    return f"{start_date}..{end_date}"

def search_rfis(
    client: Client, 
    *,
    search_text: Optional[str] = None,
    created_after: Optional[datetime]=None,
    updated_after: Optional[datetime]=None,
    limit: int = 100
    ) -> List[Dict[str, Any]]:

    collected: List[Dict[str, Any]] = []
    offset = 0

    # Create filters
    filters = {
        "status": ["open", "openRev1", "openRev2"],
        "officialResponseStatus": ["unanswered"],
    }

    filters["assignedTo"] = client.get_user_id()

    if created_after:
        filters["createdAt"] = create_date_range(start=created_after)

    if updated_after:
        filters["updatedAt"] = create_date_range(start=updated_after)

    fields_list = [
        "customIdentifier",
        "title",
        "question",
        "status",
        "createdAt",
        "dueDate",
        "attachmentsCount"
    ]

    body = {
        "limit": limit,
        "offset": offset,
        "search": search_text,
        "sort":[{
            "field": "createdAt",
            "order": "DESC"
        }],
        "filter": filters,
        "fields": fields_list
    }

    try:
        response = client.search_rfis(body=body)
    except Exception as e:
        logger.error(f"[search_rfis] Search RFIs failed with error: {e}")
        raise

    for r in response.get("results", []):
        collected.append(r)
    return collected