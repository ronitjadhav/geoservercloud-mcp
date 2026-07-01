# Migration: Fork → Standalone Package

## What changed

This repository started as a **fork** of
[`camptocamp/python-geoservercloud`](https://github.com/camptocamp/python-geoservercloud)
with the MCP server added on top. It is now a **standalone package that depends on
`geoservercloud` from PyPI**.

## Why

The MCP server only ever used the library's public `GeoServerCloud` class — it never
modified upstream code. Carrying a full copy of the library meant every upstream
release had to be pulled in with a git merge, which produced recurring conflicts
(README, `pyproject.toml`, `poetry.lock`) and the "Sync fork has conflicts" problem.

Depending on the published package removes all of that:

|                      | Before (fork)                                                   | After (dependency)                 |
| -------------------- | --------------------------------------------------------------- | ---------------------------------- |
| Get upstream updates | `git merge upstream/master` + resolve conflicts                 | `poetry add geoservercloud@latest` |
| Repo contents        | entire upstream library + our wrapper                           | only our wrapper                   |
| CI                   | upstream's full unit + acceptance suite                         | lint + smoke tests                 |
| Versioning           | `poetry-dynamic-versioning` (git tags, inherited from upstream) | static version in `pyproject.toml` |

The user-facing package name (`geoservercloud-mcp`), the CLI entry point
(`geoservercloud-mcp`), and the MCP Registry identity are unchanged.

## What was done

- Moved the server from `geoservercloud/mcp/` to a top-level `geoservercloud_mcp/`
  package. The rename avoids shadowing the installed `geoservercloud` dependency
  (a local `geoservercloud/` directory would take import precedence over the PyPI
  package and break `from geoservercloud import GeoServerCloud`).
- Rewrote `pyproject.toml`: dependencies reduced to `geoservercloud` + `fastmcp`;
  dropped the inherited upstream tooling (dynamic versioning, dependency-tweak
  plugins, the library's own deps and dev tools) and the upstream console scripts;
  set a static version.
- Removed the vendored upstream tree: `geoservercloud/` (library source),
  `geoserver_acceptance_tests/`, the library's `tests/`, `docs/source/` (Sphinx),
  `ci/`, and `Makefile`.
- Replaced CI (`.github/workflows/main.yaml`) with a lint + test job, and removed the
  Sphinx `docs.yaml` workflow (it documented the library, not this package).
- Updated the Dockerfile to copy `geoservercloud_mcp/` and actually install the
  package (so the `geoservercloud-mcp` entry point exists).
- Added smoke tests in `tests/test_server.py`.
- Kept `docs/LIBRARY.md` as a verbatim mirror of the upstream README for reference.

## Tracking upstream going forward

```bash
poetry add geoservercloud@latest   # or edit the pin in pyproject.toml, then `poetry lock`
```

New tools still require the wrapped method to exist on `GeoServerCloud` upstream; if
it doesn't, contribute it to `camptocamp/python-geoservercloud` first, then bump the
dependency here.
