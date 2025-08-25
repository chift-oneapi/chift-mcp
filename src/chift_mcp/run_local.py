import asyncio

from chift_mcp.mcp import get_mcp


async def run_mcp_async():
    mcp = await get_mcp()
    await mcp.run_async()


def main():
    """Entry point for the local MCP server."""
    asyncio.run(run_mcp_async())


if __name__ == "__main__":
    main()
