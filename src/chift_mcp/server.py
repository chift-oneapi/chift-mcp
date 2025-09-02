from fastmcp import FastMCP
from fastmcp.experimental.server.openapi import FastMCPOpenAPI
from fastmcp.server.auth import AuthProvider
from fastmcp.server.middleware import Middleware
from fastmcp.utilities.logging import get_logger
from httpx import get

from chift_mcp import (
    Chift,
    FilterToolsMiddleware,
    add_prompts,
    configure_chift,
    customize_tools,
    get_http_client,
    get_route_maps,
)

logger = get_logger(__name__)


async def create_mcp(
    url_base: str,
    name: str = "Chift API Bridge",
    chift_config: Chift | None = None,
    is_remote: bool = False,
    auth: AuthProvider | None = None,
    middleware: list[Middleware] | None = None,
) -> FastMCP:
    if not url_base:
        raise ValueError("Chift URL base is not set")

    if not is_remote and not chift_config:
        raise ValueError("Chift config is not set")

    tags_to_exclude = ["consumers", "connections"]
    route_maps = get_route_maps(tags_to_exclude)

    client = get_http_client(
        chift_config,
        url_base,
        is_remote,
    )
    consumer_id = None
    if chift_config:
        configure_chift(chift_config)
        consumer_id = chift_config.consumer_id

    openapi_spec = get(f"{url_base}/openapi.json").json()
    mcp = FastMCPOpenAPI(
        openapi_spec=openapi_spec,
        client=client,
        name=name,
        route_maps=route_maps,
        middleware=[
            *(middleware or []),
            FilterToolsMiddleware(consumer_id, is_remote),
        ],
        auth=auth,
        timeout=30,
    )

    add_prompts(mcp)

    await customize_tools(mcp, consumer_id, is_remote)  # Customize tools to modify openapi spec

    return mcp
