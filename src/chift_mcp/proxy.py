from fastmcp.server import FastMCP
from fastmcp.server.proxy import ProxyClient


def get_proxy(proxy_url: str):
    proxy = FastMCP.as_proxy(ProxyClient(transport=proxy_url))
    return proxy
