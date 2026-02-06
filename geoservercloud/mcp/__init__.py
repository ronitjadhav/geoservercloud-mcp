# GeoServer MCP - FastMCP Integration for python-geoservercloud
"""
This module provides an MCP (Model Context Protocol) server that wraps
the GeoServerCloud library, enabling natural language interactions with
GeoServer REST API.
"""

from geoservercloud.mcp.server import mcp, main

__all__ = ["mcp", "main"]
