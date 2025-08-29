import asyncio

from chift_mcp.config import Chift
from chift_mcp.mcp import create_mcp
from chift_mcp.middleware import EnvAuthMiddleware
from chift_mcp.proxy import proxy


async def configure_mcp():
    chift_config = Chift()
    mcp = await create_mcp(
        url_base=chift_config.url_base,
        name="Chift API Bridge",
        chift_config=chift_config,
        is_remote=False,
        auth=None,
        middleware=[
            EnvAuthMiddleware(chift_config.consumer_id, chift_config.function_config),
        ],
    )
    await mcp.import_server(proxy)
    return mcp


async def run_mcp_async():
    mcp = await configure_mcp()
    await mcp.run_async(transport="stdio")


def main():
    """Entry point for the local MCP server."""
    asyncio.run(run_mcp_async())


if __name__ == "__main__":
    main()
