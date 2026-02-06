"""
GeoServer MCP Server

FastMCP-based Model Context Protocol server that wraps the GeoServerCloud library,
enabling natural language interactions with GeoServer REST API.

Configuration via environment variables:
    GEOSERVER_URL: GeoServer base URL (default: http://localhost:8080/geoserver)
    GEOSERVER_USER: GeoServer username (default: admin)
    GEOSERVER_PASSWORD: GeoServer password (default: geoserver)
"""

import os
from functools import lru_cache
from typing import Any

from fastmcp import FastMCP

from geoservercloud import GeoServerCloud

# Create the MCP server
mcp = FastMCP(
    "GeoServer MCP",
    instructions="""
    GeoServer MCP provides tools for managing GeoServer via natural language.
    
    Available capabilities:
    - Workspaces: Create, list, get, delete workspaces
    - Datastores: Manage PostGIS, JNDI, PMTiles, and generic datastores
    - Feature Types: Create and manage vector layers
    - Coverage Stores: Manage raster stores and ImageMosaic
    - WMS/WMTS Stores: Cascade external WMS/WMTS services
    - Layer Groups: Create and manage layer groups
    - Styles: Upload and manage SLD styles
    - Users & Roles: Manage GeoServer security
    - ACL Rules: Configure access control
    - OGC Services: WMS GetMap, WFS GetFeature, WMTS GetTile
    
    Before using tools, ensure GeoServer connection is configured via:
    - GEOSERVER_URL environment variable
    - GEOSERVER_USER environment variable  
    - GEOSERVER_PASSWORD environment variable
    """,
)


@lru_cache(maxsize=1)
def get_geoserver_config() -> dict[str, str]:
    """Get GeoServer configuration from environment variables."""
    return {
        "url": os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver"),
        "user": os.getenv("GEOSERVER_USER", "admin"),
        "password": os.getenv("GEOSERVER_PASSWORD", "geoserver"),
    }


def get_geoserver() -> GeoServerCloud:
    """Create a GeoServerCloud client instance."""
    config = get_geoserver_config()
    return GeoServerCloud(
        url=config["url"],
        user=config["user"],
        password=config["password"],
    )


# =============================================================================
# CONNECTION & VERSION
# =============================================================================


@mcp.tool
def get_geoserver_connection_info() -> dict[str, str]:
    """
    Get current GeoServer connection information.
    Shows the configured URL and username (password is hidden).
    """
    config = get_geoserver_config()
    return {
        "url": config["url"],
        "user": config["user"],
        "password": "***hidden***",
        "status": "configured",
    }


@mcp.tool
def get_version() -> dict[str, Any]:
    """
    Get GeoServer version information.
    Returns version details about the connected GeoServer instance.
    """
    gs = get_geoserver()
    content, status = gs.get_version()
    return {"content": content, "status_code": status}


# =============================================================================
# WORKSPACES
# =============================================================================


@mcp.tool
def get_workspaces() -> dict[str, Any]:
    """
    List all GeoServer workspaces.
    Returns a list of all workspaces configured in GeoServer.
    """
    gs = get_geoserver()
    content, status = gs.get_workspaces()
    return {"workspaces": content, "status_code": status}


@mcp.tool
def get_workspace(workspace_name: str) -> dict[str, Any]:
    """
    Get details of a specific workspace.
    
    Args:
        workspace_name: Name of the workspace to retrieve
    """
    gs = get_geoserver()
    content, status = gs.get_workspace(workspace_name)
    return {"workspace": content, "status_code": status}


@mcp.tool
def create_workspace(
    workspace_name: str,
    isolated: bool = False,
) -> dict[str, Any]:
    """
    Create a new workspace in GeoServer.
    If the workspace already exists, it will be updated.
    
    Args:
        workspace_name: Name for the new workspace
        isolated: If True, workspace will be isolated (default: False)
    """
    gs = get_geoserver()
    content, status = gs.create_workspace(workspace_name, isolated=isolated)
    return {"message": content, "status_code": status}


@mcp.tool
def delete_workspace(workspace_name: str) -> dict[str, Any]:
    """
    Delete a workspace and all its contents recursively.
    WARNING: This will delete all datastores, layers, and styles in the workspace.
    
    Args:
        workspace_name: Name of the workspace to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_workspace(workspace_name)
    return {"message": content, "status_code": status}


@mcp.tool
def recreate_workspace(
    workspace_name: str,
    isolated: bool = False,
) -> dict[str, Any]:
    """
    Recreate a workspace by first deleting it if it exists, then creating it fresh.
    WARNING: This will delete all existing content in the workspace.
    
    Args:
        workspace_name: Name of the workspace
        isolated: If True, workspace will be isolated (default: False)
    """
    gs = get_geoserver()
    content, status = gs.recreate_workspace(workspace_name, isolated=isolated)
    return {"message": content, "status_code": status}


@mcp.tool
def get_workspace_wms_settings(workspace_name: str) -> dict[str, Any]:
    """
    Get WMS service settings for a workspace.
    
    Args:
        workspace_name: Name of the workspace
    """
    gs = get_geoserver()
    content, status = gs.get_workspace_wms_settings(workspace_name)
    return {"wms_settings": content, "status_code": status}


@mcp.tool
def publish_workspace(workspace_name: str) -> dict[str, Any]:
    """
    Enable and publish WMS service for a workspace with default settings.
    
    Args:
        workspace_name: Name of the workspace to publish
    """
    gs = get_geoserver()
    content, status = gs.publish_workspace(workspace_name)
    return {"message": content, "status_code": status}


@mcp.tool
def set_default_locale_for_service(
    workspace_name: str, locale: str
) -> dict[str, Any]:
    """
    Set a default language for localized WMS requests.
    
    Args:
        workspace_name: Name of the workspace
        locale: Language code (e.g., 'en', 'fr', 'de')
    """
    gs = get_geoserver()
    content, status = gs.set_default_locale_for_service(workspace_name, locale)
    return {"message": content, "status_code": status}


# =============================================================================
# DATASTORES
# =============================================================================


@mcp.tool
def get_datastores(workspace_name: str) -> dict[str, Any]:
    """
    List all datastores in a workspace.
    
    Args:
        workspace_name: Name of the workspace
    """
    gs = get_geoserver()
    content, status = gs.get_datastores(workspace_name)
    return {"datastores": content, "status_code": status}


@mcp.tool
def get_datastore(workspace_name: str, datastore_name: str) -> dict[str, Any]:
    """
    Get details of a specific datastore.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name of the datastore
    """
    gs = get_geoserver()
    content, status = gs.get_datastore(workspace_name, datastore_name)
    return {"datastore": content, "status_code": status}


@mcp.tool
def create_pg_datastore(
    workspace_name: str,
    datastore_name: str,
    pg_host: str,
    pg_port: int,
    pg_db: str,
    pg_user: str,
    pg_password: str,
    pg_schema: str = "public",
    description: str | None = None,
) -> dict[str, Any]:
    """
    Create a PostGIS datastore connection.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name for the new datastore
        pg_host: PostgreSQL host
        pg_port: PostgreSQL port
        pg_db: Database name
        pg_user: Database username
        pg_password: Database password
        pg_schema: Schema name (default: public)
        description: Optional description
    """
    gs = get_geoserver()
    content, status = gs.create_pg_datastore(
        workspace_name=workspace_name,
        datastore_name=datastore_name,
        pg_host=pg_host,
        pg_port=pg_port,
        pg_db=pg_db,
        pg_user=pg_user,
        pg_password=pg_password,
        pg_schema=pg_schema,
        description=description,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def create_jndi_datastore(
    workspace_name: str,
    datastore_name: str,
    jndi_reference: str,
    pg_schema: str = "public",
    description: str | None = None,
) -> dict[str, Any]:
    """
    Create a PostGIS datastore from a JNDI resource.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name for the new datastore
        jndi_reference: JNDI resource name
        pg_schema: Schema name (default: public)
        description: Optional description
    """
    gs = get_geoserver()
    content, status = gs.create_jndi_datastore(
        workspace_name=workspace_name,
        datastore_name=datastore_name,
        jndi_reference=jndi_reference,
        pg_schema=pg_schema,
        description=description,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def create_pmtiles_datastore(
    workspace_name: str,
    datastore_name: str,
    pmtiles_url: str,
    description: str | None = None,
) -> dict[str, Any]:
    """
    Create a PMTiles datastore.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name for the new datastore
        pmtiles_url: URL or path to the PMTiles file
        description: Optional description
    """
    gs = get_geoserver()
    content, status = gs.create_pmtiles_datastore(
        workspace_name=workspace_name,
        datastore_name=datastore_name,
        pmtiles_url=pmtiles_url,
        description=description,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def create_datastore(
    workspace_name: str,
    datastore_name: str,
    datastore_type: str,
    connection_parameters: dict[str, Any],
    description: str | None = None,
    enabled: bool = True,
) -> dict[str, Any]:
    """
    Create a generic datastore with custom connection parameters.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name for the new datastore
        datastore_type: Type (e.g., "PostGIS", "Shapefile")
        connection_parameters: Dict of connection parameters
        description: Optional description
        enabled: Enable the datastore (default: True)
    """
    gs = get_geoserver()
    content, status = gs.create_datastore(
        workspace_name=workspace_name,
        datastore_name=datastore_name,
        datastore_type=datastore_type,
        connection_parameters=connection_parameters,
        description=description,
        enabled=enabled,
    )
    return {"message": content, "status_code": status}


# =============================================================================
# WMS STORES
# =============================================================================


@mcp.tool
def get_wms_store(workspace_name: str, wms_store_name: str) -> dict[str, Any]:
    """
    Get details of a WMS store.
    
    Args:
        workspace_name: Name of the workspace
        wms_store_name: Name of the WMS store
    """
    gs = get_geoserver()
    content, status = gs.get_wms_store(workspace_name, wms_store_name)
    return {"wms_store": content, "status_code": status}


@mcp.tool
def create_wms_store(
    workspace_name: str,
    wms_store_name: str,
    capabilities_url: str,
) -> dict[str, Any]:
    """
    Create a cascaded WMS store to proxy an external WMS service.
    
    Args:
        workspace_name: Name of the workspace
        wms_store_name: Name for the new WMS store
        capabilities_url: URL to the external WMS GetCapabilities
    """
    gs = get_geoserver()
    content, status = gs.create_wms_store(
        workspace_name=workspace_name,
        wms_store_name=wms_store_name,
        capabilities_url=capabilities_url,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def delete_wms_store(workspace_name: str, wms_store_name: str) -> dict[str, Any]:
    """
    Delete a WMS store and all its layers.
    
    Args:
        workspace_name: Name of the workspace
        wms_store_name: Name of the WMS store to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_wms_store(workspace_name, wms_store_name)
    return {"message": content, "status_code": status}


@mcp.tool
def get_wms_layer(
    workspace_name: str, wms_store_name: str, wms_layer_name: str
) -> dict[str, Any]:
    """
    Get details of a WMS layer.
    
    Args:
        workspace_name: Name of the workspace
        wms_store_name: Name of the WMS store
        wms_layer_name: Name of the WMS layer
    """
    gs = get_geoserver()
    content, status = gs.get_wms_layer(workspace_name, wms_store_name, wms_layer_name)
    return {"wms_layer": content, "status_code": status}


@mcp.tool
def create_wms_layer(
    workspace_name: str,
    wms_store_name: str,
    native_layer_name: str,
    published_layer_name: str | None = None,
) -> dict[str, Any]:
    """
    Publish a layer from a cascaded WMS store.
    
    Args:
        workspace_name: Name of the workspace
        wms_store_name: Name of the WMS store
        native_layer_name: Layer name in the remote WMS
        published_layer_name: Published name (default: same as native)
    """
    gs = get_geoserver()
    content, status = gs.create_wms_layer(
        workspace_name=workspace_name,
        wms_store_name=wms_store_name,
        native_layer_name=native_layer_name,
        published_layer_name=published_layer_name,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def delete_wms_layer(
    workspace_name: str, wms_store_name: str, wms_layer_name: str
) -> dict[str, Any]:
    """
    Delete a WMS layer.
    
    Args:
        workspace_name: Name of the workspace
        wms_store_name: Name of the WMS store
        wms_layer_name: Name of the WMS layer to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_wms_layer(workspace_name, wms_store_name, wms_layer_name)
    return {"message": content, "status_code": status}


# =============================================================================
# WMTS STORES
# =============================================================================


@mcp.tool
def create_wmts_store(
    workspace_name: str,
    wmts_store_name: str,
    capabilities_url: str,
) -> dict[str, Any]:
    """
    Create a cascaded WMTS store to proxy an external WMTS service.
    
    Args:
        workspace_name: Name of the workspace
        wmts_store_name: Name for the new WMTS store
        capabilities_url: URL to the external WMTS GetCapabilities
    """
    gs = get_geoserver()
    content, status = gs.create_wmts_store(
        workspace_name=workspace_name,
        name=wmts_store_name,
        capabilities=capabilities_url,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def delete_wmts_store(workspace_name: str, wmts_store_name: str) -> dict[str, Any]:
    """
    Delete a WMTS store and all its layers.
    
    Args:
        workspace_name: Name of the workspace
        wmts_store_name: Name of the WMTS store to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_wmts_store(workspace_name, wmts_store_name)
    return {"message": content, "status_code": status}


@mcp.tool
def create_wmts_layer(
    workspace_name: str,
    wmts_store_name: str,
    native_layer_name: str,
    published_layer_name: str | None = None,
    epsg: int = 4326,
) -> dict[str, Any]:
    """
    Publish a layer from a cascaded WMTS store.
    
    Args:
        workspace_name: Name of the workspace
        wmts_store_name: Name of the WMTS store
        native_layer_name: Layer name in the remote WMTS
        published_layer_name: Published name (default: same as native)
        epsg: EPSG code for the layer (default: 4326)
    """
    gs = get_geoserver()
    content, status = gs.create_wmts_layer(
        workspace_name=workspace_name,
        wmts_store=wmts_store_name,
        native_layer=native_layer_name,
        published_layer=published_layer_name,
        epsg=epsg,
    )
    return {"message": content, "status_code": status}


# =============================================================================
# FEATURE TYPES
# =============================================================================


@mcp.tool
def get_feature_types(workspace_name: str, datastore_name: str) -> dict[str, Any]:
    """
    List all feature types (vector layers) in a datastore.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name of the datastore
    """
    gs = get_geoserver()
    content, status = gs.get_feature_types(workspace_name, datastore_name)
    return {"feature_types": content, "status_code": status}


@mcp.tool
def get_feature_type(
    workspace_name: str, datastore_name: str, feature_type_name: str
) -> dict[str, Any]:
    """
    Get details of a specific feature type.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name of the datastore
        feature_type_name: Name of the feature type
    """
    gs = get_geoserver()
    content, status = gs.get_feature_type(
        workspace_name, datastore_name, feature_type_name
    )
    return {"feature_type": content, "status_code": status}


@mcp.tool
def create_feature_type(
    layer_name: str,
    workspace_name: str,
    datastore_name: str,
    title: str | None = None,
    abstract: str | None = None,
    epsg: int = 4326,
    keywords: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a feature type (vector layer) from a database table.
    
    Args:
        layer_name: Name for the layer (must match table name)
        workspace_name: Name of the workspace
        datastore_name: Name of the datastore
        title: Human-readable title
        abstract: Layer description
        epsg: EPSG code for the SRS (default: 4326)
        keywords: List of keywords
    """
    gs = get_geoserver()
    content, status = gs.create_feature_type(
        layer_name=layer_name,
        workspace_name=workspace_name,
        datastore_name=datastore_name,
        title=title,
        abstract=abstract,
        epsg=epsg,
        keywords=keywords or [],
    )
    return {"message": content, "status_code": status}


@mcp.tool
def delete_feature_type(
    workspace_name: str, datastore_name: str, layer_name: str
) -> dict[str, Any]:
    """
    Delete a feature type and its associated layer.
    
    Args:
        workspace_name: Name of the workspace
        datastore_name: Name of the datastore
        layer_name: Name of the feature type to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_feature_type(workspace_name, datastore_name, layer_name)
    return {"message": content, "status_code": status}


# =============================================================================
# COVERAGE STORES
# =============================================================================


@mcp.tool
def get_coverages(workspace_name: str, coveragestore_name: str) -> dict[str, Any]:
    """
    List all coverages (raster layers) in a coverage store.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name of the coverage store
    """
    gs = get_geoserver()
    content, status = gs.get_coverages(workspace_name, coveragestore_name)
    return {"coverages": content, "status_code": status}


@mcp.tool
def get_coverage(
    workspace_name: str, coveragestore_name: str, coverage_name: str
) -> dict[str, Any]:
    """
    Get details of a specific coverage.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name of the coverage store
        coverage_name: Name of the coverage
    """
    gs = get_geoserver()
    content, status = gs.get_coverage(workspace_name, coveragestore_name, coverage_name)
    return {"coverage": content, "status_code": status}


@mcp.tool
def get_coverage_store(workspace_name: str, coveragestore_name: str) -> dict[str, Any]:
    """
    Get details of a coverage store.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name of the coverage store
    """
    gs = get_geoserver()
    content, status = gs.get_coverage_store(workspace_name, coveragestore_name)
    return {"coverage_store": content, "status_code": status}


@mcp.tool
def create_coverage_store(
    workspace_name: str,
    coveragestore_name: str,
    url: str,
    store_type: str = "ImageMosaic",
    enabled: bool = True,
) -> dict[str, Any]:
    """
    Create a coverage store for raster data.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name for the coverage store
        url: Path to the raster data directory or file
        store_type: Type (ImageMosaic, GeoTIFF, etc.)
        enabled: Enable the store (default: True)
    """
    gs = get_geoserver()
    content, status = gs.create_coverage_store(
        workspace_name=workspace_name,
        coveragestore_name=coveragestore_name,
        url=url,
        type=store_type,
        enabled=enabled,
    )
    return {"coverage_store": content, "status_code": status}


@mcp.tool
def create_coverage(
    workspace_name: str,
    coveragestore_name: str,
    coverage_name: str,
    title: str | None = None,
) -> dict[str, Any]:
    """
    Publish a coverage layer from a coverage store.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name of the coverage store
        coverage_name: Name for the coverage layer
        title: Human-readable title
    """
    gs = get_geoserver()
    content, status = gs.create_coverage(
        workspace_name=workspace_name,
        coveragestore_name=coveragestore_name,
        coverage_name=coverage_name,
        title=title,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def delete_coverage_store(
    workspace_name: str, coveragestore_name: str
) -> dict[str, Any]:
    """
    Delete a coverage store and all its coverages.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name of the coverage store to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_coverage_store(workspace_name, coveragestore_name)
    return {"message": content, "status_code": status}


@mcp.tool
def create_imagemosaic_store_from_directory(
    workspace_name: str, coveragestore_name: str, directory_path: str
) -> dict[str, Any]:
    """
    Create an ImageMosaic coverage store from a directory of raster files.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name for the coverage store
        directory_path: Path to the directory containing raster files
    """
    gs = get_geoserver()
    content, status = gs.create_imagemosaic_store_from_directory(
        workspace_name, coveragestore_name, directory_path
    )
    return {"message": content, "status_code": status}


@mcp.tool
def harvest_granules_to_coverage_store(
    workspace_name: str, coveragestore_name: str, directory_path: str
) -> dict[str, Any]:
    """
    Harvest additional granules (raster files) into an existing ImageMosaic store.
    
    Args:
        workspace_name: Name of the workspace
        coveragestore_name: Name of the coverage store
        directory_path: Path to directory containing new granules
    """
    gs = get_geoserver()
    content, status = gs.harvest_granules_to_coverage_store(
        workspace_name, coveragestore_name, directory_path
    )
    return {"message": content, "status_code": status}


# =============================================================================
# LAYER GROUPS
# =============================================================================


@mcp.tool
def get_layer_groups(workspace_name: str) -> dict[str, Any]:
    """
    List all layer groups in a workspace.
    
    Args:
        workspace_name: Name of the workspace
    """
    gs = get_geoserver()
    content, status = gs.get_layer_groups(workspace_name)
    return {"layer_groups": content, "status_code": status}


@mcp.tool
def get_layer_group(workspace_name: str, layer_group_name: str) -> dict[str, Any]:
    """
    Get details of a specific layer group.
    
    Args:
        workspace_name: Name of the workspace
        layer_group_name: Name of the layer group
    """
    gs = get_geoserver()
    content, status = gs.get_layer_group(workspace_name, layer_group_name)
    return {"layer_group": content, "status_code": status}


@mcp.tool
def create_layer_group(
    group_name: str,
    workspace_name: str,
    layers: list[str],
    styles: list[str] | None = None,
    title: str | None = None,
    abstract: str | None = None,
    epsg: int = 4326,
    mode: str = "SINGLE",
) -> dict[str, Any]:
    """
    Create a layer group combining multiple layers.
    
    Args:
        group_name: Name for the layer group
        workspace_name: Name of the workspace
        layers: List of layer names to include
        styles: List of style names (one per layer)
        title: Human-readable title
        abstract: Layer group description
        epsg: EPSG code (default: 4326)
        mode: Mode (SINGLE, NAMED, CONTAINER, EO)
    """
    gs = get_geoserver()
    content, status = gs.create_layer_group(
        group=group_name,
        workspace_name=workspace_name,
        layers=layers,
        styles=styles,
        title=title,
        abstract=abstract,
        epsg=epsg,
        mode=mode,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def delete_layer_group(workspace_name: str, layer_group_name: str) -> dict[str, Any]:
    """
    Delete a layer group.
    
    Args:
        workspace_name: Name of the workspace
        layer_group_name: Name of the layer group to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_layer_group(workspace_name, layer_group_name)
    return {"message": content, "status_code": status}


# =============================================================================
# STYLES
# =============================================================================


@mcp.tool
def get_styles(workspace_name: str | None = None) -> dict[str, Any]:
    """
    List all styles. If workspace is provided, list workspace styles,
    otherwise list global styles.
    
    Args:
        workspace_name: Optional workspace name
    """
    gs = get_geoserver()
    content, status = gs.get_styles(workspace_name)
    return {"styles": content, "status_code": status}


@mcp.tool
def get_style_definition(
    style_name: str, workspace_name: str | None = None
) -> dict[str, Any]:
    """
    Get the definition of a style.
    
    Args:
        style_name: Name of the style
        workspace_name: Optional workspace name
    """
    gs = get_geoserver()
    content, status = gs.get_style_definition(style_name, workspace_name)
    return {"style": content, "status_code": status}


@mcp.tool
def create_style_from_string(
    style_name: str,
    style_content: str,
    workspace_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a style from an SLD string.
    
    Args:
        style_name: Name for the new style
        style_content: SLD content as a string
        workspace_name: Optional workspace (global if not provided)
    """
    gs = get_geoserver()
    content, status = gs.create_style_from_string(
        style_name=style_name,
        style_string=style_content,
        workspace_name=workspace_name,
    )
    return {"message": content, "status_code": status}


@mcp.tool
def set_default_layer_style(
    layer_name: str, workspace_name: str, style_name: str
) -> dict[str, Any]:
    """
    Set the default style for a layer.
    
    Args:
        layer_name: Name of the layer
        workspace_name: Name of the workspace
        style_name: Name of the style to set as default
    """
    gs = get_geoserver()
    content, status = gs.set_default_layer_style(layer_name, workspace_name, style_name)
    return {"message": content, "status_code": status}


# =============================================================================
# GWC (GeoWebCache)
# =============================================================================


@mcp.tool
def get_gwc_layer(workspace_name: str, layer_name: str) -> dict[str, Any]:
    """
    Get GeoWebCache configuration for a layer.
    
    Args:
        workspace_name: Name of the workspace
        layer_name: Name of the layer
    """
    gs = get_geoserver()
    content, status = gs.get_gwc_layer(workspace_name, layer_name)
    return {"gwc_layer": content, "status_code": status}


@mcp.tool
def publish_gwc_layer(
    workspace_name: str, layer_name: str, epsg: int = 4326
) -> dict[str, Any]:
    """
    Enable tile caching for a layer in GeoWebCache.
    
    Args:
        workspace_name: Name of the workspace
        layer_name: Name of the layer
        epsg: EPSG code for the gridset (default: 4326)
    """
    gs = get_geoserver()
    content, status = gs.publish_gwc_layer(workspace_name, layer_name, epsg)
    return {"message": content, "status_code": status}


@mcp.tool
def delete_gwc_layer(workspace_name: str, layer_name: str) -> dict[str, Any]:
    """
    Remove tile caching for a layer from GeoWebCache.
    
    Args:
        workspace_name: Name of the workspace
        layer_name: Name of the layer
    """
    gs = get_geoserver()
    content, status = gs.delete_gwc_layer(workspace_name, layer_name)
    return {"message": content, "status_code": status}


@mcp.tool
def create_gridset(epsg: int) -> dict[str, Any]:
    """
    Create a gridset for GeoWebCache.
    Supported EPSG codes: 2056, 21781, 3857.
    
    Args:
        epsg: EPSG code for the gridset
    """
    gs = get_geoserver()
    content, status = gs.create_gridset(epsg)
    return {"message": content, "status_code": status}


# =============================================================================
# OGC SERVICES - WMS
# =============================================================================


@mcp.tool
def get_wms_layers(
    workspace_name: str, accept_languages: str | None = None
) -> dict[str, Any]:
    """
    Get WMS capabilities and list all layers for a workspace.
    
    Args:
        workspace_name: Name of the workspace
        accept_languages: Language preference (e.g., 'en', 'fr')
    """
    gs = get_geoserver()
    content = gs.get_wms_layers(workspace_name, accept_languages)
    return {"layers": content}


# =============================================================================
# OGC SERVICES - WFS
# =============================================================================


@mcp.tool
def get_wfs_layers(workspace_name: str) -> dict[str, Any]:
    """
    Get WFS capabilities and list all feature types for a workspace.
    
    Args:
        workspace_name: Name of the workspace
    """
    gs = get_geoserver()
    content = gs.get_wfs_layers(workspace_name)
    return {"layers": content}


@mcp.tool
def get_feature(
    workspace_name: str,
    type_name: str,
    feature_id: int | None = None,
    max_features: int | None = None,
) -> dict[str, Any]:
    """
    WFS GetFeature request to retrieve features from a layer.
    
    Args:
        workspace_name: Name of the workspace
        type_name: Feature type (layer) name
        feature_id: Optional specific feature ID
        max_features: Maximum number of features to return
    """
    gs = get_geoserver()
    content = gs.get_feature(workspace_name, type_name, feature_id, max_features)
    return {"features": content}


@mcp.tool
def describe_feature_type(
    workspace_name: str | None = None, type_name: str | None = None
) -> dict[str, Any]:
    """
    WFS DescribeFeatureType request to get schema information.
    
    Args:
        workspace_name: Optional workspace name
        type_name: Optional feature type name
    """
    gs = get_geoserver()
    content = gs.describe_feature_type(workspace_name, type_name)
    return {"schema": content}


@mcp.tool
def get_property_value(
    workspace_name: str, type_name: str, property_name: str
) -> dict[str, Any]:
    """
    WFS GetPropertyValue request to get values of a specific property.
    
    Args:
        workspace_name: Name of the workspace
        type_name: Feature type (layer) name
        property_name: Name of the property to retrieve values for
    """
    gs = get_geoserver()
    content = gs.get_property_value(workspace_name, type_name, property_name)
    return {"values": content}


# =============================================================================
# USERS & ROLES
# =============================================================================


@mcp.tool
def create_user(
    username: str, password: str, enabled: bool = True
) -> dict[str, Any]:
    """
    Create a GeoServer user.
    
    Args:
        username: Username for the new user
        password: Password for the new user
        enabled: Enable the user (default: True)
    """
    gs = get_geoserver()
    content, status = gs.create_user(username, password, enabled)
    return {"message": content, "status_code": status}


@mcp.tool
def update_user(
    username: str,
    password: str | None = None,
    enabled: bool | None = None,
) -> dict[str, Any]:
    """
    Update a GeoServer user.
    
    Args:
        username: Username to update
        password: New password (optional)
        enabled: Enable/disable the user (optional)
    """
    gs = get_geoserver()
    content, status = gs.update_user(username, password, enabled)
    return {"message": content, "status_code": status}


@mcp.tool
def delete_user(username: str) -> dict[str, Any]:
    """
    Delete a GeoServer user.
    
    Args:
        username: Username to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_user(username)
    return {"message": content, "status_code": status}


@mcp.tool
def create_role(role_name: str) -> dict[str, Any]:
    """
    Create a GeoServer role.
    
    Args:
        role_name: Name for the new role
    """
    gs = get_geoserver()
    content, status = gs.create_role(role_name)
    return {"message": content, "status_code": status}


@mcp.tool
def delete_role(role_name: str) -> dict[str, Any]:
    """
    Delete a GeoServer role.
    
    Args:
        role_name: Name of the role to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_role(role_name)
    return {"message": content, "status_code": status}


@mcp.tool
def get_user_roles(username: str) -> dict[str, Any]:
    """
    Get all roles assigned to a user.
    
    Args:
        username: Username to get roles for
    """
    gs = get_geoserver()
    content, status = gs.get_user_roles(username)
    return {"roles": content, "status_code": status}


@mcp.tool
def assign_role_to_user(username: str, role_name: str) -> dict[str, Any]:
    """
    Assign a role to a user.
    
    Args:
        username: Username
        role_name: Role to assign
    """
    gs = get_geoserver()
    content, status = gs.assign_role_to_user(username, role_name)
    return {"message": content, "status_code": status}


@mcp.tool
def remove_role_from_user(username: str, role_name: str) -> dict[str, Any]:
    """
    Remove a role from a user.
    
    Args:
        username: Username
        role_name: Role to remove
    """
    gs = get_geoserver()
    content, status = gs.remove_role_from_user(username, role_name)
    return {"message": content, "status_code": status}


# =============================================================================
# ACL RULES
# =============================================================================


@mcp.tool
def get_acl_rules() -> dict[str, Any]:
    """
    Get all GeoServer ACL data rules.
    """
    gs = get_geoserver()
    content, status = gs.get_acl_rules()
    return {"rules": content, "status_code": status}


@mcp.tool
def create_acl_rule(
    priority: int = 0,
    access: str = "DENY",
    role: str | None = None,
    user: str | None = None,
    service: str | None = None,
    request: str | None = None,
    workspace_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a GeoServer ACL data rule.
    
    Args:
        priority: Rule priority (lower = higher priority)
        access: ALLOW or DENY
        role: Role name (optional)
        user: Username (optional)
        service: Service (WMS, WFS, etc.)
        request: Request type
        workspace_name: Workspace (optional)
    """
    gs = get_geoserver()
    content, status = gs.create_acl_rule(
        priority=priority,
        access=access,
        role=role,
        user=user,
        service=service,
        request=request,
        workspace_name=workspace_name,
    )
    return {"rule": content, "status_code": status}


@mcp.tool
def create_acl_admin_rule(
    priority: int = 0,
    access: str = "ADMIN",
    role: str | None = None,
    user: str | None = None,
    workspace_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a GeoServer ACL admin rule.
    
    Args:
        priority: Rule priority
        access: Access level
        role: Role name (optional)
        user: Username (optional)
        workspace_name: Workspace (optional)
    """
    gs = get_geoserver()
    content, status = gs.create_acl_admin_rule(
        priority=priority,
        access=access,
        role=role,
        user=user,
        workspace_name=workspace_name,
    )
    return {"rule": content, "status_code": status}


@mcp.tool
def delete_acl_admin_rule(rule_id: int) -> dict[str, Any]:
    """
    Delete an ACL admin rule by ID.
    
    Args:
        rule_id: ID of the rule to delete
    """
    gs = get_geoserver()
    content, status = gs.delete_acl_admin_rule(rule_id)
    return {"message": content, "status_code": status}


@mcp.tool
def delete_all_acl_rules() -> dict[str, Any]:
    """
    Delete all ACL data rules.
    WARNING: This removes all access control rules.
    """
    gs = get_geoserver()
    content, status = gs.delete_all_acl_rules()
    return {"message": content, "status_code": status}


@mcp.tool
def delete_all_acl_admin_rules() -> dict[str, Any]:
    """
    Delete all ACL admin rules.
    WARNING: This removes all admin access control rules.
    """
    gs = get_geoserver()
    content, status = gs.delete_all_acl_admin_rules()
    return {"message": content, "status_code": status}


# =============================================================================
# ENTRY POINT
# =============================================================================


def main():
    """Main entry point for the GeoServer MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
