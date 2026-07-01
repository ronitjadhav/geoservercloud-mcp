# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This is a **fork** of `camptocamp/python-geoservercloud` that adds an MCP server on top of the library. The fork's own work lives in `geoservercloud/mcp/` (a FastMCP server) plus MCP-focused docs/packaging; everything else is the upstream `GeoServerCloud` client library that the MCP server wraps.

## Git / fork workflow (important)

- Remotes: `fork` = `ronitjadhav/geoservercloud-mcp` (ours), `upstream` = `camptocamp/python-geoservercloud` (parent).
- **Only ever push to `fork`, never to `upstream`. Never force-push** unless the user explicitly asks. Always name the remote explicitly: `git push fork master`.
- **Never use GitHub's "Sync fork" button** — it only fast-forwards and will offer to *discard* our commits. Pull upstream changes by merging instead:
  ```
  git fetch upstream && git merge upstream/master   # resolve, commit
  git push fork master
  ```
- Recurring merge-conflict resolutions: take upstream's newer version pins in `pyproject.toml` but keep `fastmcp`; keep the fork's MCP-focused `README.md` (upstream's library dev section belongs in `docs/`); regenerate `poetry.lock` with `poetry lock` rather than hand-merging.

## Commands

- Install: `make install` (`poetry lock && poetry install`)
- Unit tests + coverage: `make tests`
- Single test: `poetry run pytest tests/path_to_test.py::test_name -vvv`
- Docs (Sphinx): `make docs`
- Acceptance tests (spins up GeoServer + PostGIS via Docker, runs, tears down): `make acceptance-tests`. Sub-targets: `acceptance-tests-up`, `acceptance-tests-down`, `acceptance-tests-logs`.
- Run MCP server locally with inspector UI (http://127.0.0.1:6274): `poetry run fastmcp dev geoservercloud/mcp/server.py`
- Full dev stack (GeoServer + PostGIS + MCP): `cd mcp && docker compose up -d`
- Console entry point for the published server: `geoservercloud-mcp` → `geoservercloud.mcp:main`

Versioning is git-tag driven (`poetry-dynamic-versioning`), so the version in `pyproject.toml` is not authoritative at build time.

## Architecture

Three layers, bottom to top:

1. **`GeoServerCloud`** (`geoservercloud/geoservercloud.py`) — the core client. All GeoServer REST operations are methods on this one class. It delegates HTTP to `geoservercloud/services/` (`restclient.py`, `restservice.py`, `owsservice.py`) and (de)serializes via the dataclass-style objects in `geoservercloud/models/` (one file per resource: workspace, datastore, featuretype, style, etc.). `GeoServerCloudSync` (`geoservercloudsync.py`) copies workspaces between two instances.

2. **MCP server** (`geoservercloud/mcp/server.py`) — a `FastMCP` instance exposing ~69 `@mcp.tool`-decorated functions, each a thin wrapper over a `GeoServerCloud` method. Connection config (`url`/`user`/`password`) is held in a module-level mutable dict, seeded from `GEOSERVER_URL`/`GEOSERVER_USER`/`GEOSERVER_PASSWORD` env vars and changeable at runtime via the `configure_geoserver_connection` tool. `get_geoserver()` builds a fresh client per call from that config.

3. **Clients** — Claude Desktop, VS Code/Cursor, etc., connect over MCP.

### Adding a new MCP tool

1. Add the method to `GeoServerCloud` in `geoservercloud/geoservercloud.py`.
2. Add an `@mcp.tool`-decorated wrapper in `geoservercloud/mcp/server.py` that calls `get_geoserver()` and returns a JSON-serializable value. The docstring is what the AI assistant sees — write it for that audience.

Tools are grouped in `server.py` by banner comments (Connection, Workspaces, Datastores, Feature Types, Coverage Stores, WMS/WMTS, Layer Groups, Styles, Users & Roles, ACL, OGC Services).
