

from chift_mcp.__main__ import get_mcp


async def test_get_mcp():
    mcp = await get_mcp()
    tools = await mcp.get_tools()
    

    