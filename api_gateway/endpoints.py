#!/usr/bin/env python3
"""
HaloPSA API Endpoint Reference

Built-in knowledge of all HaloPSA API endpoints and their parameters.
No database or swagger file needed.
"""

from typing import Optional

# Complete HaloPSA API endpoint catalog
HALO_ENDPOINTS = {
    # --- Core Service Desk ---
    "Tickets": {
        "path": "/Tickets",
        "category": "Service Desk",
        "description": "Manage tickets/requests. The core endpoint for service desk operations.",
        "methods": {
            "GET /Tickets": "Search/list tickets",
            "GET /Tickets/{id}": "Get single ticket by ID",
            "POST /Tickets": "Create or update tickets (send array of ticket objects)",
            "DELETE /Tickets/{id}": "Delete a ticket",
        },
        "search_params": {
            "search": "Text search across ticket fields",
            "count": "Max results to return (default 50)",
            "pageinate": "Enable pagination (bool)",
            "page_size": "Page size when paginating",
            "page_no": "Page number",
            "order": "Field name to sort by",
            "orderdesc": "Sort descending (bool)",
            "client_id": "Filter by client ID",
            "agent_id": "Filter by agent ID",
            "status_id": "Filter by status ID",
            "user_id": "Filter by end-user ID",
            "site_id": "Filter by site ID",
            "team": "Filter by team ID",
            "tickettype_id": "Filter by ticket type",
            "open_only": "Only open tickets (bool)",
            "closed_only": "Only closed tickets (bool)",
            "contract_id": "Filter by contract",
            "asset_id": "Filter by asset",
            "priority": "Filter by priority ID",
            "category_1": "Filter by category 1",
            "category_2": "Filter by category 2",
            "category_3": "Filter by category 3",
            "category_4": "Filter by category 4",
            "view_id": "Use a saved view/filter",
            "startdate": "Filter by date range start",
            "enddate": "Filter by date range end",
            "datesearch": "Date field to filter on",
        },
        "get_params": {
            "includedetails": "Include extended details (bool, default True)",
            "includelastaction": "Include last action/note (bool)",
            "ticketidonly": "Return only ID fields (bool)",
        },
        "create_fields": {
            "summary": "Ticket subject (required)",
            "details": "Ticket description",
            "details_html": "HTML description",
            "client_id": "Client ID",
            "client_name": "Client name (alternative to client_id)",
            "user_id": "End-user ID",
            "user_name": "End-user name",
            "agent_id": "Assigned agent ID",
            "site_id": "Site ID",
            "status_id": "Status ID",
            "tickettype_id": "Ticket type ID",
            "priority_id": "Priority ID",
            "sla_id": "SLA ID",
            "parent_id": "Parent ticket ID",
            "dateoccurred": "Date occurred",
        },
    },
    "Actions": {
        "path": "/Actions",
        "category": "Service Desk",
        "description": "Manage ticket actions/notes. Actions are notes, emails, and updates on tickets.",
        "methods": {
            "GET /Actions": "Search actions (requires ticket_id or date range)",
            "GET /Actions/{id}": "Get single action",
            "POST /Actions": "Create/update actions",
        },
        "search_params": {
            "ticket_id": "Ticket ID (required unless using date range)",
            "startdate": "Start date (format: 2025-03-04T12:53:05)",
            "enddate": "End date",
            "count": "Max results",
            "agentonly": "Only agent actions (bool)",
            "conversationonly": "Only conversation actions (bool)",
            "excludesys": "Exclude system actions (bool)",
            "excludeprivate": "Exclude private actions (bool)",
            "includeattachments": "Include attachment info (bool)",
        },
        "create_fields": {
            "ticket_id": "Ticket ID (required)",
            "note": "Note text (HTML supported)",
            "outcome": "Action outcome/type",
            "hiddenfromuser": "Private/agent-only (bool)",
            "emailfrom": "Email from address",
            "emailto": "Email to address",
            "emailcc": "Email CC",
        },
    },
    "Status": {
        "path": "/Status",
        "category": "Service Desk",
        "description": "Get and manage ticket statuses.",
        "methods": {
            "GET /Status": "List statuses",
            "GET /Status/{id}": "Get single status",
            "POST /Status": "Create/update status",
        },
        "search_params": {
            "type": "Filter by type",
            "showcounts": "Show ticket counts per status (bool)",
            "domain": "Filter by domain",
            "excludepending": "Exclude pending statuses (bool)",
            "excludeclosed": "Exclude closed statuses (bool)",
        },
    },
    "TicketTypes": {
        "path": "/TicketType",
        "category": "Service Desk",
        "description": "Get and manage ticket types/categories.",
        "methods": {
            "GET /TicketType": "List ticket types",
            "GET /TicketType/{id}": "Get single ticket type",
            "POST /TicketType": "Create/update ticket type",
        },
        "search_params": {
            "client_id": "Filter by client",
            "showcounts": "Show counts (bool)",
            "domain": "Filter by domain",
            "showinactive": "Include inactive (bool)",
        },
    },

    # --- People ---
    "Clients": {
        "path": "/Client",
        "category": "People",
        "description": "Manage clients/customers/organizations.",
        "methods": {
            "GET /Client": "Search clients",
            "GET /Client/{id}": "Get single client",
            "POST /Client": "Create/update clients",
            "DELETE /Client/{id}": "Delete a client",
        },
        "search_params": {
            "search": "Text search",
            "count": "Max results (default 50)",
            "toplevel_id": "Filter by top-level org",
            "includeinactive": "Include inactive (bool)",
            "includeactive": "Include active (bool, default True)",
            "pageinate": "Enable pagination",
            "page_size": "Page size",
            "page_no": "Page number",
            "order": "Sort field",
            "orderdesc": "Sort descending",
        },
        "get_params": {
            "includedetails": "Include extended details (bool)",
            "includediagramdetails": "Include diagram details (bool)",
        },
        "create_fields": {
            "name": "Client name (required for new)",
            "toplevel_id": "Top-level org ID",
            "inactive": "Set inactive (bool)",
        },
    },
    "Users": {
        "path": "/Users",
        "category": "People",
        "description": "Manage end-users/contacts.",
        "methods": {
            "GET /Users": "Search users",
            "GET /Users/{id}": "Get single user",
            "POST /Users": "Create/update users",
            "DELETE /Users/{id}": "Delete a user",
        },
        "search_params": {
            "search": "Text search",
            "count": "Max results",
            "client_id": "Filter by client",
            "site_id": "Filter by site",
            "toplevel_id": "Filter by top-level",
            "department_id": "Filter by department",
            "asset_id": "Filter by asset",
            "includeinactive": "Include inactive (bool)",
            "includeactive": "Include active (bool)",
            "approversonly": "Only approvers (bool)",
            "excludeagents": "Exclude agents (bool)",
            "search_phonenumbers": "Search phone numbers (bool)",
        },
        "create_fields": {
            "name": "Full name",
            "firstname": "First name",
            "surname": "Last name",
            "emailaddress": "Email",
            "client_id": "Client ID",
            "site_id": "Site ID",
            "phonenumber": "Phone",
            "mobilenumber": "Mobile",
        },
    },
    "Agents": {
        "path": "/Agent",
        "category": "People",
        "description": "Manage agents/technicians.",
        "methods": {
            "GET /Agent": "List agents",
            "GET /Agent/{id}": "Get single agent",
            "POST /Agent": "Create/update agents",
        },
        "search_params": {
            "team": "Filter by team",
            "search": "Text search",
            "includedetails": "Include details (bool)",
        },
    },
    "Sites": {
        "path": "/Site",
        "category": "People",
        "description": "Manage client sites/locations.",
        "methods": {
            "GET /Site": "List sites",
            "GET /Site/{id}": "Get single site",
            "POST /Site": "Create/update sites",
        },
        "search_params": {
            "search": "Text search",
            "client_id": "Filter by client",
        },
    },
    "Teams": {
        "path": "/Team",
        "category": "People",
        "description": "Manage teams.",
        "methods": {
            "GET /Team": "List teams",
            "GET /Team/{id}": "Get single team",
            "POST /Team": "Create/update teams",
        },
    },
    "Suppliers": {
        "path": "/Supplier",
        "category": "People",
        "description": "Manage suppliers/vendors.",
        "methods": {
            "GET /Supplier": "List suppliers",
            "GET /Supplier/{id}": "Get single supplier",
            "POST /Supplier": "Create/update suppliers",
        },
    },

    # --- Assets & Configuration ---
    "Assets": {
        "path": "/Asset",
        "category": "Assets",
        "description": "Manage IT assets and configuration items.",
        "methods": {
            "GET /Asset": "Search assets",
            "GET /Asset/{id}": "Get single asset",
            "POST /Asset": "Create/update assets",
            "DELETE /Asset/{id}": "Delete an asset",
        },
        "search_params": {
            "search": "Text search",
            "count": "Max results",
            "client_id": "Filter by client",
            "site_id": "Filter by site",
            "assetgroup_id": "Filter by asset group",
            "assettype_id": "Filter by asset type",
            "linkedto_id": "Filter by linked asset",
            "ticket_id": "Filter by ticket",
            "username": "Filter by username",
            "includeinactive": "Include inactive (bool)",
            "includeactive": "Include active (bool)",
            "includechildren": "Include children (bool)",
            "contract_id": "Filter by contract",
        },
        "get_params": {
            "includedetails": "Include extended details (bool)",
            "includediagramdetails": "Include diagram (bool)",
        },
        "create_fields": {
            "client_id": "Client ID",
            "site_id": "Site ID",
            "users": "Assigned users (list)",
            "fields": "Custom fields (list)",
        },
    },
    "Attachments": {
        "path": "/Attachment",
        "category": "Assets",
        "description": "Manage file attachments on tickets, actions, etc.",
        "methods": {
            "GET /Attachment": "List attachments",
            "GET /Attachment/{id}": "Download attachment",
            "POST /Attachment": "Upload attachment",
            "DELETE /Attachment/{id}": "Delete attachment",
        },
        "search_params": {
            "ticket_id": "Filter by ticket",
            "action_id": "Filter by action (requires ticket_id)",
            "type": "Attachment type",
            "unique_id": "Specific attachment ID",
        },
    },

    # --- Projects ---
    "Projects": {
        "path": "/Projects",
        "category": "Projects",
        "description": "Manage projects.",
        "methods": {
            "GET /Projects": "List projects",
            "GET /Projects/{id}": "Get single project",
            "POST /Projects": "Create/update projects",
        },
        "search_params": {
            "search": "Text search",
            "count": "Max results",
        },
        "get_params": {
            "includedetails": "Include details (bool)",
            "includelastaction": "Include last action (bool)",
            "ticketidonly": "ID only mode (bool)",
        },
    },

    # --- Contracts & Billing ---
    "Contracts": {
        "path": "/ClientContract",
        "category": "Billing",
        "description": "Manage client contracts.",
        "methods": {
            "GET /ClientContract": "List contracts",
            "GET /ClientContract/{id}": "Get single contract",
            "POST /ClientContract": "Create/update contracts",
        },
        "search_params": {
            "search": "Text search",
            "count": "Max results",
            "pageinate": "Pagination",
            "page_size": "Page size",
            "page_no": "Page number",
        },
    },
    "Invoices": {
        "path": "/Invoice",
        "category": "Billing",
        "description": "Manage invoices.",
        "methods": {
            "GET /Invoice": "List invoices",
            "GET /Invoice/{id}": "Get single invoice",
            "POST /Invoice": "Create/update invoices",
        },
        "search_params": {
            "search": "Text search",
            "count": "Max results",
            "client_id": "Filter by client",
            "site_id": "Filter by site",
            "ticket_id": "Filter by ticket",
            "postedonly": "Only posted (bool)",
            "notpostedonly": "Only not posted (bool)",
            "includelines": "Include line items (bool)",
        },
    },
    "RecurringInvoices": {
        "path": "/RecurringInvoice",
        "category": "Billing",
        "description": "Manage recurring invoices.",
        "methods": {
            "GET /RecurringInvoice": "List recurring invoices",
            "GET /RecurringInvoice/{id}": "Get single recurring invoice",
            "POST /RecurringInvoice": "Create/update recurring invoices",
        },
        "search_params": {
            "search": "Text search",
            "count": "Max results",
            "client_id": "Filter by client",
            "includelines": "Include lines (bool)",
        },
    },
    "Items": {
        "path": "/Item",
        "category": "Billing",
        "description": "Manage billable items/products.",
        "methods": {
            "GET /Item": "List items",
            "GET /Item/{id}": "Get single item",
            "POST /Item": "Create/update items",
        },
    },
    "Quotes": {
        "path": "/Quotation",
        "category": "Billing",
        "description": "Manage quotes/quotations.",
        "methods": {
            "GET /Quotation": "List quotes",
            "GET /Quotation/{id}": "Get single quote",
            "POST /Quotation": "Create/update quotes",
        },
    },

    # --- Other ---
    "Appointments": {
        "path": "/Appointment",
        "category": "Scheduling",
        "description": "Manage appointments/calendar entries.",
        "methods": {
            "GET /Appointment": "List appointments",
            "GET /Appointment/{id}": "Get single appointment",
            "POST /Appointment": "Create/update appointments",
        },
    },
    "Opportunities": {
        "path": "/Opportunities",
        "category": "Sales",
        "description": "Manage sales opportunities.",
        "methods": {
            "GET /Opportunities": "List opportunities",
            "GET /Opportunities/{id}": "Get single opportunity",
            "POST /Opportunities": "Create/update opportunities",
        },
    },
    "KnowledgeBase": {
        "path": "/KBArticle",
        "category": "Knowledge",
        "description": "Manage knowledge base articles.",
        "methods": {
            "GET /KBArticle": "List KB articles",
            "GET /KBArticle/{id}": "Get single article",
            "POST /KBArticle": "Create/update articles",
        },
    },
    "Reports": {
        "path": "/Report",
        "category": "Reporting",
        "description": "Access and run reports.",
        "methods": {
            "GET /Report": "List reports",
            "GET /Report/{id}": "Get/run a report",
            "POST /Report": "Create/update reports",
        },
    },

    # --- Undocumented but functional ---
    "TopLevel": {
        "path": "/TopLevel",
        "category": "Organization",
        "description": "Top-level organizations/groups (undocumented).",
        "methods": {
            "GET /TopLevel": "List top-level orgs",
            "GET /TopLevel/{id}": "Get single top-level",
        },
    },
    "DistributionLists": {
        "path": "/DistributionLists",
        "category": "Communication",
        "description": "Email distribution lists (undocumented).",
        "methods": {
            "GET /DistributionLists": "List distribution lists",
            "GET /DistributionLists/{id}": "Get single list",
            "POST /DistributionLists": "Create/update lists",
        },
    },
    "Currency": {
        "path": "/Currency",
        "category": "Billing",
        "description": "Currency management (undocumented).",
        "methods": {
            "GET /Currency": "List currencies",
            "GET /Currency/{id}": "Get single currency",
        },
    },
    "SoftwareLicences": {
        "path": "/SoftwareLicence",
        "category": "Assets",
        "description": "Software licenses/subscriptions (undocumented).",
        "methods": {
            "GET /SoftwareLicence": "List licenses",
            "GET /SoftwareLicence/{id}": "Get single license",
            "POST /SoftwareLicence": "Create/update licenses",
        },
    },
    "UserRoles": {
        "path": "/UserRoles",
        "category": "People",
        "description": "User roles (undocumented).",
        "methods": {
            "GET /UserRoles": "List user roles",
            "GET /UserRoles/{id}": "Get single role",
        },
    },
    "AzureADConnection": {
        "path": "/azureadconnection",
        "category": "Integration",
        "description": "Azure AD / Entra ID connection configuration.",
        "methods": {
            "GET /azureadconnection": "List Azure AD connections",
            "POST /azureadconnection": "Create/update connections",
        },
    },
    "InvoiceChange": {
        "path": "/InvoiceChange",
        "category": "Billing",
        "description": "Invoice change tracking (undocumented).",
        "methods": {
            "GET /InvoiceChange": "Search invoice changes",
        },
        "search_params": {
            "search": "Text search",
            "invoice_id": "Filter by invoice",
            "line_id": "Filter by line item",
            "type_id": "Filter by type",
            "count": "Max results",
        },
    },
}


def search_endpoints(query: Optional[str] = None) -> str:
    """Search/list endpoints. If query is None, list categories."""
    if not query:
        categories = {}
        for name, ep in HALO_ENDPOINTS.items():
            cat = ep["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)

        lines = ["HaloPSA API \u2014 Available Categories:\n"]
        for cat in sorted(categories.keys()):
            endpoints = ", ".join(sorted(categories[cat]))
            lines.append(f"  {cat}: {endpoints}")
        lines.append("\nUse list_endpoints(category='...') to see endpoints in a category.")
        lines.append("Use get_endpoint_details(resource='...') for full details on any endpoint.")
        return "\n".join(lines)

    q = query.lower()
    matches = []
    for name, ep in HALO_ENDPOINTS.items():
        if (q in name.lower() or
            q in ep["category"].lower() or
            q in ep["description"].lower() or
            q in ep["path"].lower()):
            matches.append((name, ep))

    if not matches:
        return f"No endpoints found matching '{query}'. Use list_endpoints() to see all categories."

    lines = [f"Endpoints matching '{query}':\n"]
    for name, ep in matches:
        methods = " | ".join(ep["methods"].keys())
        lines.append(f"  {name} ({ep['category']})\n    Path: {ep['path']}\n    {ep['description']}\n    Methods: {methods}\n")
    return "\n".join(lines)


def get_endpoint_info(resource: str) -> str:
    """Get detailed info about an endpoint."""
    ep = HALO_ENDPOINTS.get(resource)
    if not ep:
        for name, e in HALO_ENDPOINTS.items():
            if name.lower() == resource.lower():
                ep = e
                resource = name
                break

    if not ep:
        return f"Unknown resource '{resource}'. Use list_endpoints() to see available endpoints."

    lines = [f"=== {resource} ==="]
    lines.append(f"Path: {ep['path']}")
    lines.append(f"Category: {ep['category']}")
    lines.append(f"Description: {ep['description']}")

    lines.append("\nMethods:")
    for method, desc in ep["methods"].items():
        lines.append(f"  {method} \u2014 {desc}")

    if "search_params" in ep:
        lines.append("\nSearch/List Parameters:")
        for param, desc in ep["search_params"].items():
            lines.append(f"  {param}: {desc}")

    if "get_params" in ep:
        lines.append("\nGet (Single Item) Parameters:")
        for param, desc in ep["get_params"].items():
            lines.append(f"  {param}: {desc}")

    if "create_fields" in ep:
        lines.append("\nCreate/Update Fields:")
        for field, desc in ep["create_fields"].items():
            lines.append(f"  {field}: {desc}")

    lines.append(f"\nNote: HaloPSA POST endpoints expect an ARRAY of objects, e.g. [{{...}}]")
    lines.append(f"All endpoints support additional undocumented parameters via extra_params dict.")

    return "\n".join(lines)
