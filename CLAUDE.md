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

After bumping, run `poetry run pytest`: the coverage guard (see "Adding a new MCP
tool") flags any new upstream methods that lack a tool.

## Working in this repo (important)

- **`master` is branch-protected.** All changes go through a PR — **you cannot
  `git push origin master` directly, and force-pushes are blocked.** A PR only merges
  once the `Lint and test` CI check is green (no approval required — self-merge is
  fine). Escape hatch if ever needed: disable the rule in Settings → Branches, or
  `gh api -X DELETE repos/ronitjadhav/geoservercloud-mcp/branches/master/protection`.
- Push only to `origin` (`ronitjadhav/geoservercloud-mcp`). There is no `upstream`
  remote anymore (the repo was detached from its fork network); never force-push
  unless explicitly asked.
- **CI runs `pre-commit` with no `SKIP`**, so every hook (black, isort, prettier,
  bandit, mypy, ripsecrets, check-dependabot, …) is enforced. Run it locally before
  pushing. `pre-commit` isn't a poetry dep; install it with
  `pip install --user --break-system-packages pre-commit` if missing.

## Docs site (`app/`)

A Vue 3 + Vite neobrutalist single-page site deployed to GitHub Pages at
`https://geoservermcp.maplabs.tech`. Source is in `app/`; it is
**not** part of the Python package.

**Keep it in sync.** Whenever you touch anything user-facing — new tools, new
install method, changed env vars, new client support — also update the relevant
copy in `app/src/App.vue`. The things most likely to drift:

- Tool count in the hero lead (`70+ REST operations`)
- The `prompts` array (example natural-language asks)
- The `features` grid (capability tiles)
- Quick-start tab commands (especially the `claude mcp add` snippet)

**Dev:**

```bash
cd app && npm install   # first time
npm run dev             # http://localhost:5173/
```

**Key files:**

- `app/src/App.vue` — all content (data arrays + template)
- `app/src/style.css` — neobrutalist design tokens and layout
- `app/public/geoservercloud-mcp.png` — logo (globe + wordmark); trimmed with Pillow

**Deploy:** `.github/workflows/pages.yaml` triggers automatically on pushes to
`master` that touch `app/**`. No manual step needed.

**Important:** All HTML attribute quotes in `App.vue` must be ASCII `"` (U+0022).
Smart/curly quotes (`"` / `"`) break Vue's template parser — an editor or
formatter can silently introduce them, causing cryptic parse errors.

## Commands

- Install: `poetry install`
- Tests: `poetry run pytest`
- Single test: `poetry run pytest tests/test_server.py::test_default_config_shape -v`
- Lint: `poetry run pre-commit run --all-files`
- Run the server (stdio) locally: `poetry run geoservercloud-mcp`
- Interactive tool inspector: `poetry run fastmcp dev src/geoservercloud_mcp/server.py` (http://127.0.0.1:6274)
- Run via module: `poetry run python -m geoservercloud_mcp`
- Full dev stack (GeoServer + PostGIS + MCP): `cd docker && docker compose up -d`

## Releasing & versioning

Publishing is fully automated by `.github/workflows/publish.yaml` (PyPI Trusted
Publishing + MCP Registry via GitHub OIDC — no stored tokens). **Versioning is
git-tag driven; the `version` in `pyproject.toml` is ignored at publish time — never
hand-bump it.**

- **Cut a release:** `git tag vX.Y.Z && git push origin vX.Y.Z` → publishes stable
  `X.Y.Z` to PyPI **and** the MCP Registry.
- **Every merge to `master`** publishes `<next-patch-above-latest-tag>.dev<run_id>`
  to both (dev builds; hidden from `pip install` without `--pre`). Docs-only changes
  (`**.md`, `docs/**`) are skipped via `paths-ignore`.

**Hard-won lesson — never version backward.** Both PyPI and the MCP Registry pick
"latest" by **semver ordering**, so publishing a _lower_ version (e.g. resetting to
`0.0.1` when `0.3.0` exists) will NOT become latest — it just sits below and is
effectively invisible. To supersede an old version, publish a **higher** one.

- **PyPI**: deleted versions are permanent — a number can never be reused, and there
  is no delete API (web UI only).
- **MCP Registry**: versions _can_ be hidden via
  `PATCH /v0.1/servers/{name}/versions/{version}/status` (`active`/`deprecated`/`deleted`,
  auth via `mcp-publisher login github-oidc`), but `isLatest` is still by semver.

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
Roles, ACL, OGC Services). Return a JSON-serializable dict — usually
`{"<thing>": content, "status_code": status}`.

`tests/test_tool_coverage.py` guards coverage: it fails if `server.py` calls a
`GeoServerCloud` method that doesn't exist, or if an upstream method is unwrapped and
not listed in `INTENTIONALLY_UNCOVERED`. Methods that return **binary bodies**
(`get_map`, `get_tile`, `get_legend_graphic`, `get_feature_info`) or take **raw
bytes** are intentionally not exposed — they don't serialize to MCP text output; add
them only with a file-path/base64 design.
