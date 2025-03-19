from mcp.server import FastMCP

from src.chift_wrapper import chift_wrapper
from src.openapi_spec.parser import openapi_parser
from src.tools.chift_mapper import ChiftMCPMapper
from src.utils import register_mcp_tools

mcp = FastMCP("Chift API Bridge")

open_api_schema = openapi_parser.parse_openapi_endpoints()

modules = ["chift.models.consumers.accounting", "chift.models.consumers.invoicing"]  # get dynamic
tool_mapper = ChiftMCPMapper(parsed_openapi=openapi_parser, modules=modules)

register_mcp_tools(mcp=mcp, tools=tool_mapper.tools, consumer=chift_wrapper.consumer)



def run()->None:
    ...