# GeoServer MCP Server

A Model Context Protocol (MCP) server that exposes [GeoServer](https://geoserver.org/) REST API functionality for natural language interaction through AI assistants like Claude, VS Code Copilot, and other MCP-compatible clients.

## About

This MCP server wraps the [python-geoservercloud](../README.md) library, exposing 80+ GeoServer operations as MCP tools. This enables AI assistants to manage GeoServer workspaces, datastores, layers, styles, and more through natural language commands.

### Example Interactions

Once connected, you can ask your AI assistant things like:

- *"List all workspaces in GeoServer"*
- *"Create a new workspace called 'test_data'"*
- *"What layers are available in the 'topp' workspace?"*
- *"Create a PostGIS datastore connection"*

---

## Quick Start

### Option 1: Full Local Development Stack

Start the MCP server with a local GeoServer and PostGIS:

```bash
cd mcp
docker compose up -d
```

This starts:
- **geoservercloud-mcp**: The MCP server on port 8000
- **geoserver**: GeoServer instance on port 8080
- **postgis**: PostGIS database on port 5433

### Option 2: MCP Server Only (Connect to External GeoServer)

If you have an existing GeoServer:

```bash
cd mcp
GEOSERVER_URL=http://your-geoserver:8080/geoserver \
GEOSERVER_USER=admin \
GEOSERVER_PASSWORD=your-password \
docker compose up -d geoservercloud-mcp
```

---

## Connecting to AI Clients

### VS Code / Cursor

1. Open Command Palette → **"MCP: Add Server"**
2. Select **"Command (stdio)"**
3. Enter command: `poetry run geoservercloud-mcp`
4. Enter server ID: `geoserver`

VS Code will create an MCP configuration file. Update it with the working directory and environment variables:

```json
{
  "servers": {
    "geoserver": {
      "type": "stdio",
      "command": "poetry",
      "args": ["run", "geoservercloud-mcp"],
      "cwd": "/path/to/python-geoservercloud",
      "env": {
        "GEOSERVER_URL": "http://localhost:8080/geoserver",
        "GEOSERVER_USER": "admin",
        "GEOSERVER_PASSWORD": "geoserver"
      }
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "geoserver": {
      "command": "poetry",
      "args": ["run", "geoservercloud-mcp"],
      "cwd": "/path/to/python-geoservercloud",
      "env": {
        "GEOSERVER_URL": "http://localhost:8080/geoserver",
        "GEOSERVER_USER": "admin",
        "GEOSERVER_PASSWORD": "geoserver"
      }
    }
  }
}
```

Restart Claude Desktop after saving the configuration.

---

## Testing with FastMCP Inspector

The MCP server includes a built-in inspector UI for debugging:

```bash
# From project root
poetry install
poetry run fastmcp dev geoservercloud/mcp/server.py
```

Open http://127.0.0.1:6274 in your browser to test individual tools.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEOSERVER_URL` | `http://localhost:8080/geoserver` | GeoServer base URL |
| `GEOSERVER_USER` | `admin` | GeoServer username |
| `GEOSERVER_PASSWORD` | `geoserver` | GeoServer password |

---

## Docker Commands

```bash
# Start all services
cd mcp
docker compose up -d

# Stop services
docker compose down

# Stop and remove volumes (data)
docker compose down -v

# View logs
docker compose logs -f geoservercloud-mcp
```

---

## Python Library

This MCP server is built on the **python-geoservercloud** library. For programmatic access without MCP, see the [library documentation](../README.md).

```python
from geoservercloud import GeoServerCloud

geoserver = GeoServerCloud(
    url="http://localhost:8080/geoserver",
    user="admin",
    password="geoserver",
)
geoserver.create_workspace("my_workspace")
```

Full documentation: <https://camptocamp.github.io/python-geoservercloud/>
