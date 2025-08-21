from fastmcp.experimental.server.openapi import MCPType, RouteMap

from chift_mcp.utils.utils import CONNECTION_TYPES

base_route_maps = [
    # Exclude all routes not starting with /consumers
    RouteMap(pattern=r"^(?!\/consumers).*", mcp_type=MCPType.EXCLUDE),
    # Exclude routes containing /syncs, /integrations, /webhooks, /datastores, /issues, /datastore
    RouteMap(pattern=r".*\/syncs.*", mcp_type=MCPType.EXCLUDE),
    RouteMap(pattern=r".*\/integrations.*", mcp_type=MCPType.EXCLUDE),
    RouteMap(pattern=r".*\/webhooks.*", mcp_type=MCPType.EXCLUDE),
    RouteMap(pattern=r".*\/datastores.*", mcp_type=MCPType.EXCLUDE),
    RouteMap(pattern=r".*\/issues.*", mcp_type=MCPType.EXCLUDE),
    RouteMap(pattern=r".*\/datastore.*", mcp_type=MCPType.EXCLUDE),
]  # TODO Filter further the routes that can be exposed from consumers


def get_route_maps(tags_to_exclude: list[str]) -> list[RouteMap]:
    route_maps = [*base_route_maps]
    for tag, mcp_tag in CONNECTION_TYPES.items():
        if mcp_tag in tags_to_exclude:
            route_maps.append(RouteMap(tags={tag}, mcp_tags={mcp_tag}, mcp_type=MCPType.EXCLUDE))
            continue

        route_maps.append(RouteMap(tags={tag}, mcp_tags={mcp_tag}, mcp_type=MCPType.TOOL))

    return route_maps
