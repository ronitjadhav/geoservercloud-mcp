<!-- mcp-name: io.github.ronitjadhav/geoservercloud-mcp -->

![GeoServer MCP](app/public/geoservercloud-mcp.png)

An MCP server that wraps the [python-geoservercloud](https://github.com/camptocamp/python-geoservercloud) library, exposing 80+ GeoServer operations as natural-language tools for AI assistants like Claude, VS Code Copilot, and other MCP-compatible clients.

Once connected, you can just ask:

- _"List all workspaces in GeoServer"_
- _"Create a new workspace called `test_data`"_
- _"Publish the `roads` table from my PostGIS database"_

## Quick start (Claude Code)

One command — no manual install, `uvx` fetches and runs the server for you.

**Simplest — no credentials up front:**

```bash
claude mcp add geoserver -- uvx geoservercloud-mcp
```

The AI will ask you for the GeoServer URL, username, and password when it first
needs them. Great for trying it out or switching between servers.

**Or set the connection up front:**

```bash
claude mcp add geoserver \
  --env GEOSERVER_URL=http://localhost:8080/geoserver \
  --env GEOSERVER_USER=admin \
  --env GEOSERVER_PASSWORD=geoserver \
  -- uvx geoservercloud-mcp
```

That's it — start Claude Code and ask it to list your workspaces to confirm
it's connected.

Manage it later with `claude mcp list`, `claude mcp get geoserver`, or
`claude mcp remove geoserver`. Add `--scope user` to the add command to make it
available in every project instead of just this one.

---

## Other clients

<details>
<summary><b>Claude Desktop</b></summary>

Add this to your config file, then restart Claude Desktop:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

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

</details>

<details>
<summary><b>VS Code / Cursor</b></summary>

Add this to `.vscode/mcp.json`:

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

</details>

<details>
<summary><b>Install manually (pip / uvx)</b></summary>

```bash
# with pip
pip install geoservercloud-mcp
geoservercloud-mcp

# or run without installing (requires uv: https://docs.astral.sh/uv/)
uvx geoservercloud-mcp
```

Published to the [MCP Registry](https://registry.modelcontextprotocol.io) as
`io.github.ronitjadhav/geoservercloud-mcp`.

</details>

---

## Environment variables

| Variable             | Default                           | Description        |
| -------------------- | --------------------------------- | ------------------ |
| `GEOSERVER_URL`      | `http://localhost:8080/geoserver` | GeoServer base URL |
| `GEOSERVER_USER`     | `admin`                           | GeoServer username |
| `GEOSERVER_PASSWORD` | `geoserver`                       | GeoServer password |

All three are optional — if you skip them, you can configure the connection at
runtime by asking the AI.

---

## Development

Want to run it from source or contribute?

```bash
git clone https://github.com/ronitjadhav/geoservercloud-mcp.git
cd geoservercloud-mcp

poetry install                    # set up the environment
poetry run pytest                 # run the tests
poetry run geoservercloud-mcp     # run the server (stdio)
```

Need a GeoServer to test against? `cd docker && docker compose up -d` spins up
GeoServer + PostGIS + the MCP server.

For the full workflow — adding new tools, linting, releasing, and how publishing
works — see the **[Developer Guide](docs/DEVELOPER.md)**.

---

## Python library

This server is built on the **python-geoservercloud** library. For programmatic
access without MCP:

```python
from geoservercloud import GeoServerCloud

geoserver = GeoServerCloud(
    url="http://localhost:8080/geoserver",
    user="admin",
    password="geoserver",
)
geoserver.create_workspace("my_workspace")
```

Full library docs: <https://camptocamp.github.io/python-geoservercloud/>
