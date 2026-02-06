# Developer Guide

This guide covers the development workflow for the GeoServer MCP Server.

## Project Structure

```
python-geoservercloud/
├── geoservercloud/
│   ├── mcp/
│   │   ├── __init__.py      # Package exports
│   │   └── server.py        # MCP server implementation
│   └── geoservercloud.py    # Core GeoServer client library
├── mcp/
│   ├── Dockerfile           # MCP server container
│   └── docker-compose.yml   # Full development stack
├── server.json              # MCP Registry metadata
├── pyproject.toml           # Package configuration
└── README.md
```

## Local Development

### Prerequisites

- Python 3.10+
- Poetry
- Docker & Docker Compose

### Setup

```bash
# Install dependencies
poetry install

# Start development stack (GeoServer + PostGIS + MCP)
cd mcp
docker compose up -d

# Run MCP inspector for testing
poetry run fastmcp dev geoservercloud/mcp/server.py
```

Open http://127.0.0.1:6274 to test individual MCP tools.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEOSERVER_URL` | `http://localhost:8080/geoserver` | GeoServer base URL |
| `GEOSERVER_USER` | `admin` | GeoServer username |
| `GEOSERVER_PASSWORD` | `geoserver` | GeoServer password |

## Adding New MCP Tools

The MCP server wraps the `GeoServerCloud` class. To add a new tool:

1. Add the method to `geoservercloud/geoservercloud.py`
2. Add the `@mcp.tool()` decorated wrapper in `geoservercloud/mcp/server.py`

Example:

```python
@mcp.tool()
def my_new_tool(param1: str, param2: int) -> str:
    """Description shown to AI assistants."""
    result = gs.my_new_method(param1, param2)
    return str(result)
```

## Publishing Updates

### 1. Bump Version

```bash
poetry version patch  # 0.1.0 → 0.1.1
# or
poetry version minor  # 0.1.0 → 0.2.0
```

### 2. Update server.json

Update the `version` field to match the new version:

```json
{
  "version": "0.1.1",
  "packages": [
    {
      "version": "0.1.1"
    }
  ]
}
```

### 3. Publish to PyPI

```bash
poetry build
poetry publish
```

### 4. Publish to MCP Registry

```bash
mcp-publisher login github
mcp-publisher publish
```

## Docker Configuration

### GeoServer Extensions

The docker-compose includes:
- **MBStyle** (stable) - Mapbox Style support
- **PMTiles** (community) - PMTiles datastore

The PMTiles extension requires GeoServer 3.0.x nightly build.

### Port Mappings

| Service | Port |
|---------|------|
| MCP Server | 8000 |
| GeoServer | 8080 |
| PostGIS | 5433 |

## Testing with AI Clients

### Claude Desktop

Add to `~/.config/Claude/claude_desktop_config.json`:

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

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "geoserver": {
      "type": "stdio",
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

## Troubleshooting

### Port Conflicts

If port 5432 is in use, the docker-compose uses 5433 for PostGIS.

### Poetry Build Fails

If `poetry install` fails with README errors, ensure you use `--no-root`:

```bash
poetry install --no-root
```

### MCP Registry Publishing Fails

Common issues:
- **Version mismatch**: `server.json` version must match PyPI version
- **Missing mcp-name**: README must contain `<!-- mcp-name: io.github.username/package -->`
- **Authentication**: Re-run `mcp-publisher login github` if tokens expire
