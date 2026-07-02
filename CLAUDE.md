# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A standalone **MCP server** that exposes GeoServer's REST API as ~76 natural-language
tools for AI assistants. It is a thin wrapper over the
[`python-geoservercloud`](https://github.com/camptocamp/python-geoservercloud)
library, which it depends on **as a PyPI package** (`geoservercloud`) — it does not
vendor or modify it.

## Tracking upstream

The library is a normal dependency in `pyproject.toml` (`geoservercloud = ">=0.8.7"`).
To pick up upstream changes there is no merge — just bump the dependency:

```
poetry add geoservercloud@latest   # or edit the pin, then `poetry lock`
```

- Push only to `origin` (`ronitjadhav/geoservercloud-mcp`); never to `upstream`, and
  never force-push unless explicitly asked.

## Commands

- Install: `poetry install`
- Tests: `poetry run pytest`
- Single test: `poetry run pytest tests/test_server.py::test_default_config_shape -v`
- Lint: `poetry run pre-commit run --all-files`
- Run the server (stdio) locally: `poetry run geoservercloud-mcp`
- Interactive tool inspector: `poetry run fastmcp dev src/geoservercloud_mcp/server.py` (http://127.0.0.1:6274)
- Run via module: `poetry run python -m geoservercloud_mcp`
- Full dev stack (GeoServer + PostGIS + MCP): `cd docker && docker compose up -d`

Versioning is **git-tag driven** (see `.github/workflows/publish.yaml`): pushing a
`v*` tag publishes that stable version; merges to `master` publish `<next-patch>.dev<run_id>`.
The `version` in `pyproject.toml` is ignored at publish time — never hand-bump it.

## Architecture

Two layers:

1. **`geoservercloud` (PyPI dependency)** — the `GeoServerCloud` client class with all
   the actual GeoServer REST logic. We do not vendor or modify it.
2. **`src/geoservercloud_mcp/server.py`** — a `FastMCP` instance whose `@mcp.tool`
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
`@mcp.tool` function in `src/geoservercloud_mcp/server.py`:

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
