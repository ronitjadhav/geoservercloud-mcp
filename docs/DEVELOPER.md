# Developer Guide

This guide covers the development workflow for the GeoServer MCP Server.

## Project Structure

```
geoservercloud-mcp/
├── geoservercloud_mcp/
│   ├── __init__.py          # Package exports (mcp, main)
│   └── server.py            # MCP server implementation (FastMCP tools)
├── mcp/
│   ├── Dockerfile           # MCP server container
│   └── docker-compose.yml   # Full development stack (GeoServer + PostGIS + MCP)
├── tests/                   # Smoke tests
├── docs/                    # This guide, the library README mirror, migration notes
├── server.json              # MCP Registry metadata
├── pyproject.toml           # Package configuration
└── README.md
```

The actual GeoServer REST logic lives in the upstream `geoservercloud` library,
which this package depends on via PyPI (see `pyproject.toml`). We only maintain the
MCP wrapper in `geoservercloud_mcp/`.

## Prerequisites

- Python 3.10+
- Poetry
- Docker & Docker Compose (only for the local GeoServer stack)

## Setup

```bash
git clone https://github.com/ronitjadhav/geoservercloud-mcp
cd geoservercloud-mcp
python3 -m venv .venv
source .venv/bin/activate
poetry install
```

The `.venv` (gitignored) keeps the environment inside the project so editors pick it
up automatically. Alternatively, skip the venv steps and let Poetry manage its own
environment — then prefix commands with `poetry run`.

## Updating the Upstream Library

The GeoServer client comes from the `geoservercloud` PyPI package. To pick up
upstream changes, bump the dependency — there is no fork to merge:

```bash
poetry add geoservercloud@latest   # or edit the pin in pyproject.toml, then `poetry lock`
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

Run the smoke tests:

```bash
poetry run pytest
```

### MCP Inspector

Run individual tools interactively without an AI client:

```bash
poetry run fastmcp dev geoservercloud_mcp/server.py
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

Use `poetry run` with `cwd` pointing at the project instead of the published `uvx`
package. Replace `/path/to/geoservercloud-mcp` with your actual path.

VS Code / Cursor (`.vscode/mcp.json`):

```json
{
  "servers": {
    "geoserver": {
      "type": "stdio",
      "command": "poetry",
      "args": ["run", "geoservercloud-mcp"],
      "cwd": "/path/to/geoservercloud-mcp",
      "env": {
        "GEOSERVER_URL": "http://localhost:8080/geoserver",
        "GEOSERVER_USER": "admin",
        "GEOSERVER_PASSWORD": "geoserver"
      }
    }
  }
}
```

Claude Desktop (`~/.config/Claude/claude_desktop_config.json`) uses the same values
under `mcpServers` instead of `servers`.

To test the **published** package instead of local code, swap the command to `"uvx"`
with `"args": ["geoservercloud-mcp"]`.

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

Each tool wraps a method that already exists on the upstream `GeoServerCloud` class.
Add an `@mcp.tool` decorated wrapper in `geoservercloud_mcp/server.py`:

```python
@mcp.tool
def my_new_tool(param1: str) -> dict:
    """Description shown to AI assistants."""
    gs = get_geoserver()
    content, status = gs.some_method(param1)
    return {"content": content, "status_code": status}
```

If the method does not exist upstream, contribute it to
`camptocamp/python-geoservercloud` first, then bump the dependency.

## Publishing Updates

Versioning is static — bump it manually in both `pyproject.toml` and `server.json`.

1. **Bump the version:**

   ```bash
   poetry version patch   # 0.2.0 → 0.2.1  (or `minor`)
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
- **MCP Registry publish fails** — the `server.json` version must match the PyPI
  version; the README must contain the `<!-- mcp-name: io.github.username/package -->`
  marker; re-run `mcp-publisher login github` if tokens have expired.
