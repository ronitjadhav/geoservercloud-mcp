# Developer Guide

This guide covers the development workflow for the GeoServer MCP Server.

## Project Structure

```
python-geoservercloud/
├── geoservercloud/
│   ├── mcp/
│   │   ├── __init__.py      # Package exports
│   │   └── server.py        # MCP server implementation (FastMCP tools)
│   └── geoservercloud.py    # Core GeoServer client library (wrapped by the tools)
├── mcp/
│   ├── Dockerfile           # MCP server container
│   └── docker-compose.yml   # Full development stack
├── server.json              # MCP Registry metadata
├── pyproject.toml           # Package configuration
└── README.md
```

## Prerequisites

- Python 3.10+
- Poetry
- Docker & Docker Compose

## Setup

```bash
poetry install
```

## Development Stack

The `mcp/docker-compose.yml` runs GeoServer, PostGIS, and the MCP server together.

```bash
cd mcp
docker compose up -d          # start
docker compose ps             # status
docker compose logs -f geoserver-mcp   # logs
docker compose down           # stop
docker compose down -v        # stop and wipe all data (fresh start)
```

| Service    | URL / Port                                                |
| ---------- | --------------------------------------------------------- |
| MCP Server | http://localhost:8000                                     |
| GeoServer  | http://localhost:8080/geoserver                           |
| PostGIS    | localhost:5433 (mapped from 5432 to avoid host conflicts) |

**GeoServer extensions** included in the image:

- **MBStyle** (stable) — Mapbox Style support
- **PMTiles** (community) — PMTiles datastore; requires a GeoServer 3.0.x nightly build

## Testing the MCP Server

### MCP Inspector

Run individual tools interactively without an AI client:

```bash
poetry run fastmcp dev geoservercloud/mcp/server.py
```

Open http://127.0.0.1:6274.

### Environment Variables

| Variable             | Default                           | Description        |
| -------------------- | --------------------------------- | ------------------ |
| `GEOSERVER_URL`      | `http://localhost:8080/geoserver` | GeoServer base URL |
| `GEOSERVER_USER`     | `admin`                           | GeoServer username |
| `GEOSERVER_PASSWORD` | `geoserver`                       | GeoServer password |

If these are unset, the server starts unconfigured and the AI client can set the
connection at runtime via `configure_geoserver_connection()` (see "Dynamic
Configuration" below).

### Connecting an AI Client to Local Code

Use `poetry run` with `cwd` pointing at the project instead of the published
`uvx` package. Replace `/path/to/python-geoservercloud` with your actual path.

VS Code / Cursor (`.vscode/mcp.json`):

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

Claude Desktop (`~/.config/Claude/claude_desktop_config.json`) uses the same
values under `mcpServers` instead of `servers`.

To test the **published** package instead of local code, swap the command to
`"uvx"` with `"args": ["geoservercloud-mcp"]`.

### Dynamic Configuration (No Environment Variables)

Omit the `env` section entirely and the AI will:

1. Check the connection via `get_geoserver_connection_info()`
2. Ask you for the GeoServer URL, username, and password
3. Call `configure_geoserver_connection(url, user, password)` to set it

```json
{
  "servers": {
    "geoserver": {
      "command": "uvx",
      "args": ["geoservercloud-mcp"]
    }
  }
}
```

Useful when working with multiple GeoServer instances.

## Adding New MCP Tools

The MCP server wraps the `GeoServerCloud` class. To add a new tool:

1. Add the method to `geoservercloud/geoservercloud.py`
2. Add an `@mcp.tool` decorated wrapper in `geoservercloud/mcp/server.py`

```python
@mcp.tool
def my_new_tool(param1: str, param2: int) -> str:
    """Description shown to AI assistants."""
    gs = get_geoserver()
    return str(gs.my_new_method(param1, param2))
```

## Publishing Updates

The fork manages its version manually in both `pyproject.toml` and `server.json`.

1. **Bump the version:**

   ```bash
   poetry version patch   # 0.1.0 → 0.1.1  (or `minor`)
   ```

2. **Update `server.json`** — set both the top-level `version` and the
   `packages[].version` to match.

3. **Publish to PyPI:**

   ```bash
   poetry build
   poetry publish
   ```

4. **Publish to the MCP Registry:**

   ```bash
   mcp-publisher login github
   mcp-publisher publish
   ```

## Troubleshooting

- **Port conflicts** — PostGIS is mapped to 5433 to avoid clashing with a host
  PostgreSQL on 5432.
- **Poetry build fails on README** — run `poetry install --no-root`.
- **MCP Registry publish fails** — the `server.json` version must match the PyPI
  version; the README must contain the `<!-- mcp-name: io.github.username/package -->`
  marker; re-run `mcp-publisher login github` if tokens have expired.
