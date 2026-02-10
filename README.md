# HaloPSA API Gateway MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with the HaloPSA API. Built for Claude Desktop to interact with HaloPSA — search tickets, manage clients, execute API calls, and more.

## Features

- 🔐 **OAuth2 Authentication** — Client credentials flow with automatic token refresh
- 🎫 **Smart Ticket Tools** — Search, create, update tickets and add actions with dedicated tools
- 👥 **Client & User Management** — Search clients, users, agents, sites
- 📦 **Asset Management** — Search and manage assets
- 📋 **Project & Contract Tools** — Search projects, contracts, invoices
- 🔧 **Generic API Access** — Execute any HaloPSA API call with `execute_api_call`
- 💾 **Fast Memory** — Save frequently used queries for instant reuse
- 📚 **Built-in Endpoint Reference** — No database or swagger file needed — all 29 endpoints documented inline

## Architecture

Unlike traditional approaches that require downloading a swagger.json and building a database, this server has the complete HaloPSA API endpoint catalog built right in. This means:

- **No database build step** — works immediately after install
- **No swagger file needed** — endpoint reference is always available
- **Pure Python** — no Node.js wrapper layer
- **Smart tools** for common operations + generic tools for anything else

## Installation

### Prerequisites

- Python 3.10+
- `pip` package manager

### Quick Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/jasondsmith72/HALO-PSA-API-Gateway-MCP.git
   cd HALO-PSA-API-Gateway-MCP
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Claude Desktop** — Add to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "halo-psa-api": {
         "command": "python",
         "args": ["C:/path/to/HALO-PSA-API-Gateway-MCP/halo_api_gateway_server.py"],
         "env": {
           "HALO_BASE_URL": "https://yourtenant.halopsa.com",
           "HALO_CLIENT_ID": "your-client-id",
           "HALO_CLIENT_SECRET": "your-client-secret",
           "HALO_TENANT": "yourtenant",
           "HALO_SCOPE": "all"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** and the MCP server will be available.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `HALO_BASE_URL` | Yes | Your HaloPSA instance URL (e.g. `https://yourtenant.halopsa.com`) |
| `HALO_CLIENT_ID` | Yes | OAuth2 Client ID from HaloPSA API application |
| `HALO_CLIENT_SECRET` | Yes | OAuth2 Client Secret |
| `HALO_TENANT` | No* | Tenant name (required for cloud-hosted instances) |
| `HALO_AUTH_URL` | No | Override auth token URL (defaults to `{BASE_URL}/auth/token`) |
| `HALO_SCOPE` | No | API scope (defaults to `all`) |

## Getting API Credentials

1. Login to HaloPSA → **Configuration** → **Integrations** → **HaloPSA API**
2. Click **View Applications** → **New**
3. Set **Authentication Method** to `Client ID and Secret (Services)`
4. Set **Login Type** to `Agent` and select an agent account
5. Under **Permissions**, set to `all` (or configure specific permissions)
6. Save and note your **Client ID** and **Client Secret**

## Available Tools (22 total)

### Smart Tools (High-Level)
| Tool | Description |
|---|---|
| `search_tickets` | Search tickets with filters (client, agent, status, etc.) |
| `get_ticket` | Get a single ticket by ID |
| `create_ticket` | Create a new ticket |
| `update_ticket` | Update an existing ticket |
| `add_action_to_ticket` | Add a note/action to a ticket |
| `search_clients` | Search clients/customers |
| `get_client` | Get a single client by ID |
| `search_users` | Search end-users/contacts |
| `search_assets` | Search IT assets |
| `search_agents` | Search agents/technicians |
| `search_projects` | Search projects |
| `search_contracts` | Search contracts |
| `search_invoices` | Search invoices |

### Generic Tools (Power User)
| Tool | Description |
|---|---|
| `execute_api_call` | Execute any HaloPSA API call with full control |
| `send_raw_api_request` | Send raw API request string (e.g. `GET /Tickets?open_only=true`) |

### Reference Tools
| Tool | Description |
|---|---|
| `list_endpoints` | Browse available API endpoints by category |
| `get_endpoint_details` | Get detailed info about any endpoint |

### Fast Memory Tools
| Tool | Description |
|---|---|
| `save_to_fast_memory` | Save a query for quick reuse |
| `list_fast_memory` | List saved queries |
| `delete_from_fast_memory` | Delete a saved query |
| `clear_fast_memory` | Clear all saved queries |

## Usage Examples

In Claude Desktop, you can ask:

- *"Show me all open tickets for client ID 42"*
- *"Create a ticket for MicroTech USA about a VPN issue"*
- *"Search for all assets belonging to client 15"*
- *"What agents do we have?"*
- *"Add a note to ticket 1234 saying the issue has been resolved"*
- *"List all HaloPSA API endpoints"*
- *"Show me details about the Tickets endpoint"*
- *"Execute GET /Tickets with open_only=true and count=5"*

## Project Structure

```
HALO-PSA-API-Gateway-MCP/
├── halo_api_gateway_server.py    # Main entry point
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── api_gateway/
    ├── __init__.py
    ├── server.py                  # MCP server implementation
    ├── endpoints.py               # Built-in API endpoint reference (29 endpoints)
    └── fast_memory_db.py          # Fast Memory storage
```

## License

UNLICENSED — Private use

## Author

Jason Smith — MicroTech USA
