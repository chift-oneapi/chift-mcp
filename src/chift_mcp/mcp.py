from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger
from httpx import get

from chift_mcp.config import Chift
from chift_mcp.http_client import get_http_client
from chift_mcp.middleware import FilterToolsMiddleware, UserAuthMiddleware
from chift_mcp.prompts import add_prompts
from chift_mcp.route_maps import get_route_maps
from chift_mcp.tools import customize_tools, register_consumer_tools
from chift_mcp.utils.utils import configure_chift

chift_config = Chift()

base_url = chift_config.url_base
logger = get_logger(__name__)


async def get_mcp(name: str = "Chift API Bridge"):
    if not base_url:
        raise ValueError("Chift URL base is not set")

    tags_to_exclude = ["consumers", "connections"]
    route_maps = get_route_maps(tags_to_exclude)

    client = get_http_client(
        client_id=chift_config.client_id,
        client_secret=chift_config.client_secret,
        account_id=chift_config.account_id,
        base_url=base_url,
    )

    configure_chift(chift_config)
    consumer_id = chift_config.consumer_id

    openapi_spec = get(f"{base_url}/openapi.json").json()
    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name=name,
        route_maps=route_maps,
        middleware=[
            UserAuthMiddleware(consumer_id, chift_config.function_config),
            FilterToolsMiddleware(),
        ],
    )

    add_prompts(mcp)

    if not consumer_id:  # Add tools allowing to list all consumers and connections
        register_consumer_tools(mcp)

    await customize_tools(
        mcp, consumer_id, chift_config.is_remote
    )  # Customize tools to modify openapi spec

    return mcp
