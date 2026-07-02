# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A standalone **MCP server** that exposes GeoServer's REST API as ~69 natural-language
tools for AI assistants. It is a thin wrapper over the upstream
[`python-geoservercloud`](https://github.com/camptocamp/python-geoservercloud)
library, which it depends on **as a PyPI package** (`geoservercloud`), not as a fork.

This repo was originally a fork of `camptocamp/python-geoservercloud`; it was
migrated to a standalone package (see `docs/MIGRATION.md`) so upstream updates are a
version bump instead of a merge, and then fully detached from the fork network into
its own standalone GitHub repo. It is no longer a fork. The primary git remote is
`origin`; `upstream` is kept only for refreshing `docs/LIBRARY.md`.

## Tracking upstream

The library is a normal dependency in `pyproject.toml` (`geoservercloud = ">=0.8.7"`).
To pick up upstream changes:

```
poetry add geoservercloud@latest   # or edit the pin, then `poetry lock`
```

No git merge, no conflict resolution. If upstream's README changed and you want the
mirror current, refresh `docs/LIBRARY.md` from it (it is a verbatim copy kept for
reference since our top-level README is MCP-focused).

- Push only to the `fork` remote (`ronitjadhav/geoservercloud-mcp`); never to
  `upstream`, and never force-push unless explicitly asked.

## Commands

- Install: `poetry install`
- Tests: `poetry run pytest`
- Single test: `poetry run pytest tests/test_server.py::test_default_config_shape -v`
- Lint: `poetry run pre-commit run --all-files`
- Run the server (stdio) locally: `poetry run geoservercloud-mcp`
- Interactive tool inspector: `poetry run fastmcp dev geoservercloud_mcp/server.py` (http://127.0.0.1:6274)
- Full dev stack (GeoServer + PostGIS + MCP): `cd mcp && docker compose up -d`

Versioning is **static** in `pyproject.toml` — bump it manually and mirror the value
into `server.json` when publishing.

## Architecture

Two layers:

1. **`geoservercloud` (PyPI dependency)** — the `GeoServerCloud` client class with all
   the actual GeoServer REST logic. We do not vendor or modify it.
2. **`geoservercloud_mcp/server.py`** — a `FastMCP` instance whose `@mcp.tool`
   functions each call `get_geoserver()` (which builds a `GeoServerCloud` from the
   current config) and return JSON-serializable results. Connection config is a
   module-level mutable dict seeded from `GEOSERVER_URL`/`GEOSERVER_USER`/
   `GEOSERVER_PASSWORD`, and changeable at runtime via the
   `configure_geoserver_connection` tool. `main()` (the `geoservercloud-mcp` entry
   point) just calls `mcp.run()`.

The package is named `geoservercloud_mcp` (not `geoservercloud.mcp`) specifically to
avoid shadowing the installed `geoservercloud` dependency.

### Adding a new MCP tool

The wrapped method must already exist on `GeoServerCloud` upstream. Add an
`@mcp.tool` function in `geoservercloud_mcp/server.py`:

```python
@mcp.tool
def my_new_tool(param1: str) -> dict:
    """Description shown to AI assistants."""
    gs = get_geoserver()
    content, status = gs.some_method(param1)
    return {"content": content, "status_code": status}
```

Tools are grouped in `server.py` by banner comments (Connection, Workspaces,
Datastores, Feature Types, Coverage Stores, WMS/WMTS, Layer Groups, Styles, Users &
Roles, ACL, OGC Services).
