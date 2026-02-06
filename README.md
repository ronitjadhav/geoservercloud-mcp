# GeoServer MCP Server

<!-- mcp-name: io.github.ronitjadhav/geoservercloud-mcp -->

A Model Context Protocol (MCP) server that exposes [GeoServer](https://geoserver.org/) REST API functionality for natural language interaction through AI assistants like Claude, VS Code Copilot, and other MCP-compatible clients.

## About

This MCP server wraps the [python-geoservercloud](docs/LIBRARY.md) library, exposing 80+ GeoServer operations as MCP tools. This enables AI assistants to manage GeoServer workspaces, datastores, layers, styles, and more through natural language commands.

### Example Interactions

Once connected, you can ask your AI assistant things like:

- *"List all workspaces in GeoServer"*
- *"Create a new workspace called 'test_data'"*
- *"What layers are available in the 'topp' workspace?"*
- *"Create a PostGIS datastore connection"*

---

## Installation

### From PyPI

```bash
pip install geoservercloud-mcp
```

Or use `uvx` to run without installing (requires [uv](https://docs.astral.sh/uv/)):

```bash
# Install uv first (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the MCP server
uvx geoservercloud-mcp
```

### From MCP Registry

This server is published to the [MCP Registry](https://registry.modelcontextprotocol.io) as:

```text
io.github.ronitjadhav/geoservercloud-mcp
```

---

## Connecting to AI Clients

### VS Code / Cursor

Add to your MCP configuration (`.vscode/mcp.json`):

```json
{
  "servers": {
    "geoserver": {
      "command": "uvx",
      "args": ["geoservercloud-mcp"],
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
      "command": "uvx",
      "args": ["geoservercloud-mcp"],
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

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEOSERVER_URL` | `http://localhost:8080/geoserver` | GeoServer base URL |
| `GEOSERVER_USER` | `admin` | GeoServer username |
| `GEOSERVER_PASSWORD` | `geoserver` | GeoServer password |

---

## Python Library

This MCP server is built on the **python-geoservercloud** library. For programmatic access without MCP, see the [library documentation](docs/LIBRARY.md).

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

---

## Development

For local development, testing, and publishing, see the [Developer Guide](docs/DEVELOPER.md).
