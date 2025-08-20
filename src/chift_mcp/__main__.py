import asyncio

import chift

from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger
from httpx import get

from chift_mcp.config import (
    config,
)
from chift_mcp.http_client import get_http_client
from chift_mcp.prompts import add_prompts
from chift_mcp.route_maps import get_route_maps
from chift_mcp.tools import customize_tools, register_consumer_tools
from chift_mcp.utils.parse_openapi_deps import resolve_openapi_refs
from chift_mcp.utils.utils import get_connection_types

base_url = config.chift.url_base
logger = get_logger(__name__)


def configure_chift(chift_config) -> None:
    """Configure global Chift client settings."""
    chift.client_secret = chift_config.client_secret
    chift.client_id = chift_config.client_id
    chift.account_id = chift_config.account_id
    chift.url_base = chift_config.url_base


async def get_mcp(name: str = "Chift API Bridge"):
    if not base_url:
        raise ValueError("Chift URL base is not set")

    tags_to_exclude = ["consumers", "connections"]
    route_maps = get_route_maps(tags_to_exclude)

    client = get_http_client(
        client_id=config.chift.client_id,
        client_secret=config.chift.client_secret,
        account_id=config.chift.account_id,
        base_url=base_url,
    )

    configure_chift(config.chift)
    consumer_id = config.chift.consumer_id
    connection_types = get_connection_types(config.chift.consumer_id)

    openapi_spec = get(f"{base_url}/openapi.json").json()
    openapi_spec = resolve_openapi_refs(openapi_spec)
    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name=name,
        # mcp_component_fn=customize_components,
        route_maps=route_maps,
        include_tags=set(connection_types),
    )

    add_prompts(mcp)
    if not consumer_id:
        register_consumer_tools(mcp)

    await customize_tools(mcp, consumer_id)

    return mcp

async def main():
    mcp = await get_mcp()
    await mcp.run_async()

if __name__ == "__main__":
    asyncio.run(main())