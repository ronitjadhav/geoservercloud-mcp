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

PyPI publishing is automated by `.github/workflows/publish.yaml` via PyPI
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no stored token):

- **Every merge to `master`** publishes a dev pre-release `X.Y.Z.devN` (where
  `X.Y.Z` is the `pyproject.toml` version and `N` is the unique GitHub Actions run
  id — always increasing, so builds never collide even if the repo is recreated).
  Dev releases are hidden from `pip install` unless `--pre` is passed.
- **Pushing a `v*` tag** publishes the stable `X.Y.Z` from `pyproject.toml`.

### Version convention

Keep `pyproject.toml` set to the **next** target version so dev builds sort ahead
of the last release. To cut release `0.3.0`:

```bash
poetry version 0.3.0                 # if not already there
# update server.json version + packages[].version to 0.3.0, commit
git tag v0.3.0 && git push fork v0.3.0   # -> publishes stable 0.3.0
poetry version 0.4.0                 # start the next dev cycle; commit
# subsequent merges publish 0.4.0.dev1, 0.4.0.dev2, ...
```

### One-time PyPI setup (Trusted Publishing)

On <https://pypi.org/manage/project/geoservercloud-mcp/settings/publishing/>, add a
GitHub trusted publisher: owner `ronitjadhav`, repo `geoservercloud-mcp`, workflow
`publish.yaml` (leave environment blank). Until this is configured the publish job
will fail auth.

### MCP Registry

Also automated in `publish.yaml`, for **both** dev and stable builds: after the PyPI
job, a second job syncs `server.json`'s version to the just-published version and
publishes to the MCP Registry via `mcp-publisher` with GitHub OIDC (`github-oidc`).
No setup or token needed — the `io.github.ronitjadhav/*` namespace is authorized
automatically for this repo.

> **Note:** unlike PyPI, the MCP Registry has no hidden-pre-release concept, so a
> published `X.Y.Z.devN` sorts newer than the last stable and becomes the registry's
> `isLatest`. If you don't want dev builds surfacing to clients that discover via the
> registry, gate this job to tags with `if: startsWith(github.ref, 'refs/tags/')`.

To publish manually if ever needed:

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
