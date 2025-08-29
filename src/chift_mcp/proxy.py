from fastmcp.server import FastMCP
from fastmcp.server.proxy import ProxyClient

proxy = FastMCP.as_proxy(ProxyClient(transport="https://docs.chift.eu/mcp"))
