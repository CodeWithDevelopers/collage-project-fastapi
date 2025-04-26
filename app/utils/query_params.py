from fastapi import Query, Request
from typing import Optional, List, Dict, Any, Tuple
import pymongo

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 10
DEFAULT_SORT_ORDER = "desc"

async def parse_listing_params(
    request: Request,
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query(DEFAULT_SORT_ORDER, regex="^(asc|desc)$"),
    select: Optional[str] = Query(None),
) -> Dict[str, Any]:
    query_params = dict(request.query_params)
    filter_params = {
        k: v for k, v in query_params.items()
        if k not in {"page", "limit", "sort_by", "sort_order", "select"}
    }

    # Field projection
    projection = None
    if select:
        projection = {field: 1 for field in select.split(",")}

    return {
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "filters": filter_params,
        "projection": projection
    }


def get_sort_criteria(sort: Optional[str]) -> List[Tuple[str, int]]:
    if not sort:
        return []
    criteria = []
    for field in sort.split(","):
        if field.startswith("-"):
            criteria.append((field[1:], -1))
        else:
            criteria.append((field, 1))
    return criteria


def get_projection(fields: Optional[str]) -> Optional[dict]:
    if not fields:
        return None  # Fetch all fields

    selected_fields = {field: 1 for field in fields.split(",")}

    # Always include required fields for schema
    required_fields = ["id", "name", "email", "role"]
    for field in required_fields:
        selected_fields[field] = 1

    # Exclude MongoDB's _id field unless explicitly requested
    selected_fields["_id"] = 0

    return selected_fields


