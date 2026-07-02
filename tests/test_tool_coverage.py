"""Guard tests for MCP tool coverage of the GeoServerCloud client."""

import inspect
import re

from geoservercloud import GeoServerCloud

import geoservercloud_mcp.server as server

# GeoServerCloud methods deliberately NOT exposed as MCP tools:
#   - internal client setup that returns None / mutates state, not a REST op
#   - raw-bytes input that can't sensibly be passed through an MCP tool arg
#   - operations that return binary image bodies (no useful text representation)
INTENTIONALLY_UNCOVERED = {
    "cleanup",  # resets client-side default workspace/datastore state
    "create_wms",  # instantiates an internal OWSLib WMS object
    "create_wmts",  # instantiates an internal OWSLib WMTS object
    "create_imagemosaic_store_from_properties_zip",  # takes raw zip bytes
    "get_map",  # returns a raster image body
    "get_tile",  # returns a raster tile body
    "get_legend_graphic",  # returns an image body
    "get_feature_info",  # returns an OWSLib ResponseWrapper
}


def _called_client_methods() -> set[str]:
    src = inspect.getsource(server)
    return set(re.findall(r"\bgs\.(\w+)\s*\(", src))


def _public_client_methods() -> set[str]:
    return {
        n
        for n, _ in inspect.getmembers(GeoServerCloud, predicate=inspect.isfunction)
        if not n.startswith("_")
    }


def test_no_phantom_client_calls():
    """Every gs.<method>() the server calls must exist on GeoServerCloud."""
    phantom = _called_client_methods() - _public_client_methods()
    assert (
        not phantom
    ), f"server.py calls non-existent GeoServerCloud methods: {phantom}"


def test_coverage_is_complete_except_known_skips():
    """Fail if a new upstream method is unwrapped and not explicitly skipped."""
    uncovered = _public_client_methods() - _called_client_methods()
    unexpected = uncovered - INTENTIONALLY_UNCOVERED
    assert not unexpected, (
        f"New GeoServerCloud methods lack an MCP tool: {sorted(unexpected)}. "
        f"Add a tool or list them in INTENTIONALLY_UNCOVERED."
    )
