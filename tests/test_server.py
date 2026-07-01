"""Smoke tests for the standalone MCP package.

These verify the repackaging is intact: the package imports (which requires the
`geoservercloud` dependency to resolve), the entry point is wired up, and the
runtime connection config behaves.
"""

from geoservercloud_mcp import main, mcp
from geoservercloud_mcp import server


def test_entrypoint_and_server_object():
    assert callable(main)
    assert mcp is not None


def test_default_config_shape():
    cfg = server.get_geoserver_config()
    assert {"url", "user", "password", "configured"}.issubset(cfg)


def test_get_geoserver_uses_config():
    # get_geoserver builds a client from the current config without connecting
    server._geoserver_config["url"] = "http://example:8080/geoserver"
    client = server.get_geoserver()
    assert "example:8080" in client.url
