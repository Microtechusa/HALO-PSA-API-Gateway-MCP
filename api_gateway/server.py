#!/usr/bin/env python3
"""
HaloPSA API Gateway MCP Server

A Model Context Protocol server for HaloPSA API integration.
Features:
- OAuth2 client credentials authentication with auto-refresh
- Smart high-level tools for common operations
- Generic API execution for any endpoint
- Built-in endpoint reference (no database needed)
- Fast Memory for saving frequently used queries
"""

import os
import sys
import json
import time
import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import FastMCP
from api_gateway.fast_memory_db import FastMemoryDB
from api_gateway.endpoints import HALO_ENDPOINTS, search_endpoints, get_endpoint_info

# Logging
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, "halo_api_gateway.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger("halo_api_gateway")

# Initialize MCP
mcp = FastMCP("halo_api_gateway")

# --- Global State ---
HALO_BASE_URL = None
HALO_AUTH_URL = None
HALO_CLIENT_ID = None
HALO_CLIENT_SECRET = None
HALO_TENANT = None
HALO_SCOPE = "all"

_access_token = None
_token_expires_at = 0

FAST_MEMORY_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fast_memory_halo.db")
fast_memory_db = None
current_query_from_fast_memory = False


# ============================================================
# Configuration & Authentication
# ============================================================

def setup_config():
    """Load configuration from environment variables."""
    global HALO_BASE_URL, HALO_AUTH_URL, HALO_CLIENT_ID, HALO_CLIENT_SECRET, HALO_TENANT, HALO_SCOPE

    HALO_BASE_URL = os.environ.get('HALO_BASE_URL', '').rstrip('/')
    HALO_CLIENT_ID = os.environ.get('HALO_CLIENT_ID')
    HALO_CLIENT_SECRET = os.environ.get('HALO_CLIENT_SECRET')
    HALO_TENANT = os.environ.get('HALO_TENANT', '')
    HALO_SCOPE = os.environ.get('HALO_SCOPE', 'all')

    HALO_AUTH_URL = os.environ.get('HALO_AUTH_URL', '')
    if not HALO_AUTH_URL and HALO_BASE_URL:
        HALO_AUTH_URL = f"{HALO_BASE_URL}/auth/token"

    logger.info("HaloPSA Configuration:")
    logger.info(f"  BASE_URL:  {HALO_BASE_URL}")
    logger.info(f"  AUTH_URL:  {HALO_AUTH_URL}")
    logger.info(f"  CLIENT_ID: {HALO_CLIENT_ID}")
    logger.info(f"  SECRET:    {'*' * len(HALO_CLIENT_SECRET) if HALO_CLIENT_SECRET else 'MISSING'}")
    logger.info(f"  TENANT:    {HALO_TENANT or '(not set)'}")
    logger.info(f"  SCOPE:     {HALO_SCOPE}")

    if not all([HALO_BASE_URL, HALO_CLIENT_ID, HALO_CLIENT_SECRET]):
        logger.warning("HaloPSA configuration incomplete — API calls will fail until env vars are set.")
        return False
    return True


async def get_access_token() -> str:
    """Get a valid OAuth2 access token, refreshing if needed."""
    global _access_token, _token_expires_at

    if _access_token and time.time() < _token_expires_at - 60:
        return _access_token

    if not HALO_AUTH_URL or not HALO_CLIENT_ID or not HALO_CLIENT_SECRET:
        raise RuntimeError(
            "HaloPSA API credentials not configured. "
            "Set HALO_BASE_URL, HALO_CLIENT_ID, and HALO_CLIENT_SECRET environment variables."
        )

    payload = {
        'grant_type': 'client_credentials',
        'client_id': HALO_CLIENT_ID,
        'client_secret': HALO_CLIENT_SECRET,
        'scope': HALO_SCOPE,
    }
    if HALO_TENANT:
        payload['tenant'] = HALO_TENANT

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(HALO_AUTH_URL, data=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    _access_token = data['access_token']
    _token_expires_at = time.time() + data.get('expires_in', 3600)
    logger.info("OAuth2 token acquired/refreshed successfully.")
    return _access_token


# ============================================================
# Core API Request Helper
# ============================================================

async def halo_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
) -> Any:
    """Make an authenticated request to the HaloPSA API."""
    token = await get_access_token()
    url = f"{HALO_BASE_URL}/api{endpoint}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    logger.info(f"API {method.upper()} {url}")
    if params:
        logger.info(f"  params: {json.dumps(params)}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.request(method.upper(), url, headers=headers, params=params, json=data)
            logger.info(f"  status: {resp.status_code}")
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text[:500]}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise RuntimeError(f"Request failed: {e}")


def format_response(result: Any) -> str:
    """Format API response for display. Always returns ALL items with no truncation."""
    if isinstance(result, dict):
        record_count = result.get('record_count', None)
        list_key = None
        list_data = None
        for k, v in result.items():
            if isinstance(v, list) and k != 'record_count':
                list_key = k
                list_data = v
                break

        if list_data is not None:
            total = record_count if record_count is not None else len(list_data)
            return f"Retrieved {total} items:\n\n{json.dumps(list_data, indent=2)}"

        return json.dumps(result, indent=2)

    elif isinstance(result, list):
        return f"Retrieved {len(result)} items:\n\n{json.dumps(result, indent=2)}"

    return json.dumps(result, indent=2)


# ============================================================
# Fast Memory
# ============================================================

def initialize_fast_memory():
    global fast_memory_db
    try:
        fast_memory_db = FastMemoryDB(FAST_MEMORY_DB_PATH)
        return True
    except Exception as e:
        logger.error(f"Fast Memory init error: {e}")
        return False


def check_fast_memory(path: str, method: str):
    global fast_memory_db, current_query_from_fast_memory
    if not fast_memory_db:
        initialize_fast_memory()
    if not fast_memory_db:
        return None
    query = fast_memory_db.find_query(path, method)
    if query:
        current_query_from_fast_memory = True
        fast_memory_db.increment_usage(query['id'])
        return query
    current_query_from_fast_memory = False
    return None


# ============================================================
# MCP TOOLS — Smart High-Level Tools
# ============================================================

@mcp.tool()
async def search_tickets(
    search: Optional[str] = None,
    client_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    status_id: Optional[int] = None,
    open_only: Optional[bool] = None,
    count: int = 50,
    order: Optional[str] = None,
    orderdesc: Optional[bool] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA tickets with common filters.

    Args:
        search: Text search across ticket fields
        client_id: Filter by client ID
        agent_id: Filter by assigned agent ID
        status_id: Filter by status ID
        open_only: If True, only return open tickets
        count: Max results (default 50)
        order: Field name to sort by
        orderdesc: True for descending sort
        extra_params: Any additional HaloPSA API parameters as a dict
    """
    params = {"count": count}
    if search: params["search"] = search
    if client_id: params["client_id"] = client_id
    if agent_id: params["agent_id"] = agent_id
    if status_id: params["status_id"] = status_id
    if open_only: params["open_only"] = True
    if order: params["order"] = order
    if orderdesc is not None: params["orderdesc"] = orderdesc
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/Tickets", params=params)
    return format_response(result)


@mcp.tool()
async def get_ticket(ticket_id: int, includedetails: bool = True, includelastaction: bool = False) -> str:
    """
    Get a single HaloPSA ticket by ID.

    Args:
        ticket_id: The ticket ID
        includedetails: Include full details (default True)
        includelastaction: Include the last action/note
    """
    params = {"includedetails": includedetails, "includelastaction": includelastaction}
    result = await halo_request("GET", f"/Tickets/{ticket_id}", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_ticket(
    summary: str,
    details: Optional[str] = None,
    client_id: Optional[int] = None,
    user_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    tickettype_id: Optional[int] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new HaloPSA ticket.

    Args:
        summary: Ticket subject/summary (required)
        details: Ticket description/body
        client_id: Client ID to assign the ticket to
        user_id: End-user ID
        agent_id: Agent to assign
        tickettype_id: Ticket type ID
        status_id: Initial status ID
        priority_id: Priority ID
        extra_fields: Any additional fields as a dict
    """
    ticket = {"summary": summary}
    if details: ticket["details"] = details
    if client_id: ticket["client_id"] = client_id
    if user_id: ticket["user_id"] = user_id
    if agent_id: ticket["agent_id"] = agent_id
    if tickettype_id: ticket["tickettype_id"] = tickettype_id
    if status_id: ticket["status_id"] = status_id
    if priority_id: ticket["priority_id"] = priority_id
    if extra_fields: ticket.update(extra_fields)

    result = await halo_request("POST", "/Tickets", data=[ticket])
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_ticket(
    ticket_id: int,
    summary: Optional[str] = None,
    details: Optional[str] = None,
    status_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Update an existing HaloPSA ticket.

    Args:
        ticket_id: Ticket ID to update (required)
        summary: New summary/subject
        details: New details
        status_id: New status ID
        agent_id: New assigned agent ID
        extra_fields: Any additional fields as a dict
    """
    ticket = {"id": ticket_id}
    if summary: ticket["summary"] = summary
    if details: ticket["details"] = details
    if status_id: ticket["status_id"] = status_id
    if agent_id: ticket["agent_id"] = agent_id
    if extra_fields: ticket.update(extra_fields)

    result = await halo_request("POST", "/Tickets", data=[ticket])
    return json.dumps(result, indent=2)


@mcp.tool()
async def add_action_to_ticket(
    ticket_id: int,
    note: str,
    outcome: str = "note",
    agent_only: bool = False,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Add a note/action to a HaloPSA ticket.

    Args:
        ticket_id: Ticket ID
        note: The note/action text (HTML supported)
        outcome: Action outcome type (default 'note')
        agent_only: If True, note is private/agent-only
        extra_fields: Any additional fields
    """
    action = {
        "ticket_id": ticket_id,
        "note": note,
        "outcome": outcome,
        "hiddenfromuser": agent_only,
    }
    if extra_fields: action.update(extra_fields)

    result = await halo_request("POST", "/Actions", data=[action])
    return json.dumps(result, indent=2)


@mcp.tool()
async def search_clients(
    search: Optional[str] = None,
    toplevel_id: Optional[int] = None,
    includeinactive: bool = False,
    count: int = 50,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA clients/customers.

    Args:
        search: Text search
        toplevel_id: Filter by top-level org ID
        includeinactive: Include inactive clients
        count: Max results
        extra_params: Additional API parameters
    """
    params = {"count": count, "includeinactive": includeinactive}
    if search: params["search"] = search
    if toplevel_id: params["toplevel_id"] = toplevel_id
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/Client", params=params)
    return format_response(result)


@mcp.tool()
async def get_client(client_id: int, includedetails: bool = True) -> str:
    """
    Get a single HaloPSA client by ID.

    Args:
        client_id: The client ID
        includedetails: Include extended details
    """
    params = {"includedetails": includedetails}
    result = await halo_request("GET", f"/Client/{client_id}", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def search_users(
    search: Optional[str] = None,
    client_id: Optional[int] = None,
    site_id: Optional[int] = None,
    count: int = 50,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA users (end-users/contacts).

    Args:
        search: Text search
        client_id: Filter by client ID
        site_id: Filter by site ID
        count: Max results
        extra_params: Additional API parameters
    """
    params = {"count": count}
    if search: params["search"] = search
    if client_id: params["client_id"] = client_id
    if site_id: params["site_id"] = site_id
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/Users", params=params)
    return format_response(result)


@mcp.tool()
async def search_assets(
    search: Optional[str] = None,
    client_id: Optional[int] = None,
    assettype_id: Optional[int] = None,
    count: int = 50,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA assets.

    Args:
        search: Text search
        client_id: Filter by client ID
        assettype_id: Filter by asset type ID
        count: Max results
        extra_params: Additional API parameters
    """
    params = {"count": count}
    if search: params["search"] = search
    if client_id: params["client_id"] = client_id
    if assettype_id: params["assettype_id"] = assettype_id
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/Asset", params=params)
    return format_response(result)


@mcp.tool()
async def search_agents(
    search: Optional[str] = None,
    team: Optional[str] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA agents (technicians).

    Args:
        search: Text search
        team: Filter by team name
        extra_params: Additional API parameters
    """
    params = {}
    if search: params["search"] = search
    if team: params["team"] = team
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/Agent", params=params)
    return format_response(result)


@mcp.tool()
async def search_projects(
    search: Optional[str] = None,
    count: int = 50,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA projects.

    Args:
        search: Text search
        count: Max results
        extra_params: Additional API parameters
    """
    params = {"count": count}
    if search: params["search"] = search
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/Projects", params=params)
    return format_response(result)


@mcp.tool()
async def search_contracts(
    search: Optional[str] = None,
    count: int = 50,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA contracts.

    Args:
        search: Text search
        count: Max results
        extra_params: Additional API parameters
    """
    params = {"count": count}
    if search: params["search"] = search
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/ClientContract", params=params)
    return format_response(result)


@mcp.tool()
async def search_invoices(
    client_id: Optional[int] = None,
    postedonly: Optional[bool] = None,
    count: int = 50,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Search HaloPSA invoices.

    Args:
        client_id: Filter by client
        postedonly: Only show posted invoices
        count: Max results
        extra_params: Additional API parameters
    """
    params = {"count": count}
    if client_id: params["client_id"] = client_id
    if postedonly is not None: params["postedonly"] = postedonly
    if extra_params: params.update(extra_params)

    result = await halo_request("GET", "/Invoice", params=params)
    return format_response(result)


# ============================================================
# MCP TOOLS — Generic / Power-User Tools
# ============================================================

@mcp.tool()
async def execute_api_call(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
) -> str:
    """
    Execute any HaloPSA API call directly.

    Args:
        endpoint: API endpoint path (e.g. /Tickets, /Client/123, /Actions)
        method: HTTP method (GET, POST, DELETE)
        params: Query parameters dict
        data: Request body (for POST — should be a list of objects per HaloPSA convention)
    """
    global current_query_from_fast_memory

    fm = check_fast_memory(endpoint, method)
    if fm:
        if params is None and fm.get('params'):
            params = fm['params']
        if data is None and fm.get('data'):
            data = fm['data']

    try:
        result = await halo_request(method, endpoint, params=params, data=data)
        response = format_response(result)

        if current_query_from_fast_memory:
            current_query_from_fast_memory = False
            response = f"[Fast Memory: {fm['description']}]\n\n{response}"
        else:
            response += (
                f"\n\n--- To save this query to Fast Memory ---\n"
                f"save_to_fast_memory(path=\"{endpoint}\", method=\"{method}\", "
                f"description=\"YOUR DESCRIPTION\""
                f"{f', params={json.dumps(params)}' if params else ''}"
                f"{f', data={json.dumps(data)}' if data else ''})"
            )

        return response
    except Exception as e:
        current_query_from_fast_memory = False
        return f"Error: {e}"


@mcp.tool()
async def send_raw_api_request(raw_request: str) -> str:
    """
    Send a raw API request string.

    Args:
        raw_request: Format \"METHOD /endpoint?params [JSON body]\"
                     Examples:
                       \"GET /Tickets?open_only=true&count=10\"
                       \"POST /Tickets [{\"summary\":\"Test ticket\"}]\"
    """
    parts = raw_request.strip().split(' ', 2)
    if len(parts) < 2:
        return "Error: Use format 'METHOD /endpoint [JSON body]'"

    method = parts[0].upper()
    path_with_params = parts[1]

    params = {}
    if '?' in path_with_params:
        path, qs = path_with_params.split('?', 1)
        for pair in qs.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v
    else:
        path = path_with_params

    data = None
    if len(parts) > 2:
        try:
            data = json.loads(parts[2])
        except json.JSONDecodeError:
            return f"Error: Invalid JSON body: {parts[2]}"

    return await execute_api_call(path, method, params or None, data)


# ============================================================
# MCP TOOLS — Endpoint Reference
# ============================================================

@mcp.tool()
async def list_endpoints(category: Optional[str] = None) -> str:
    """
    List available HaloPSA API endpoints.

    Args:
        category: Filter by category (e.g. 'tickets', 'clients', 'assets').
                  Leave empty to see all categories.
    """
    return search_endpoints(category)


@mcp.tool()
async def get_endpoint_details(resource: str) -> str:
    """
    Get detailed info about a specific HaloPSA API resource/endpoint.

    Args:
        resource: Resource name (e.g. 'Tickets', 'Clients', 'Assets', 'Actions')
    """
    return get_endpoint_info(resource)


# ============================================================
# MCP TOOLS — Fast Memory
# ============================================================

@mcp.tool()
async def save_to_fast_memory(
    path: str,
    method: str,
    description: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
) -> str:
    """
    Save an API query to Fast Memory for quick reuse.

    Args:
        path: API endpoint path
        method: HTTP method
        description: Friendly description
        params: Query parameters to save
        data: Request body to save
    """
    if not fast_memory_db:
        initialize_fast_memory()
    if not fast_memory_db:
        return "Error: Could not initialize Fast Memory."
    try:
        qid = fast_memory_db.save_query(description, path, method, params, data)
        return f"Saved to Fast Memory (ID {qid}): {description}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def list_fast_memory(search_term: Optional[str] = None) -> str:
    """
    List saved Fast Memory queries.

    Args:
        search_term: Optional filter
    """
    if not fast_memory_db:
        initialize_fast_memory()
    if not fast_memory_db:
        return "Error: Could not initialize Fast Memory."

    queries = fast_memory_db.search_queries(search_term) if search_term else fast_memory_db.get_all_queries()
    if not queries:
        return "No queries saved in Fast Memory." if not search_term else f"No queries matching '{search_term}'."

    lines = []
    for q in queries:
        lines.append(
            f"ID {q['id']}: {q['description']}\n"
            f"  {q['method'].upper()} {q['path']}  (used {q['usage_count']}x)"
        )
    return "Fast Memory queries:\n\n" + "\n\n".join(lines)


@mcp.tool()
async def delete_from_fast_memory(query_id: int) -> str:
    """Delete a query from Fast Memory by ID."""
    if not fast_memory_db:
        initialize_fast_memory()
    if not fast_memory_db:
        return "Error: Could not initialize Fast Memory."
    if fast_memory_db.delete_query(query_id):
        return f"Deleted query ID {query_id}."
    return f"No query found with ID {query_id}."


@mcp.tool()
async def clear_fast_memory() -> str:
    """Clear all Fast Memory queries."""
    if not fast_memory_db:
        initialize_fast_memory()
    if not fast_memory_db:
        return "Error: Could not initialize Fast Memory."
    count = fast_memory_db.clear_all()
    return f"Cleared {count} queries from Fast Memory."


# ============================================================
# Main
# ============================================================

def main():
    logger.info("Starting HaloPSA API Gateway MCP Server...")
    setup_config()
    initialize_fast_memory()
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
