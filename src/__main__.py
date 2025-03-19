import chift
from mcp.server import FastMCP

from src.config import config
from src.openapi_spec.parser import openapi_parser
from src.tools.chift_mapper import ChiftMCPMapper
from src.utils import (
    map_connections_to_modules,
    register_mcp_tools,
)

chift.client_secret = config.chift.client_secret
chift.client_id = config.chift.client_id
chift.account_id = config.chift.account_id
chift.url_base = config.chift.url_base
consumer = chift.Consumer.get(config.chift.consumer_id)
connections = consumer.Connection.all()

mcp = FastMCP("Chift API Bridge")

open_api_schema = openapi_parser.parse_openapi_endpoints()

modules = map_connections_to_modules(connections=connections)
tool_mapper = ChiftMCPMapper(parsed_openapi=open_api_schema, modules=list(modules))
tool_mapper.analyze_models().create_mcp_tools()
register_mcp_tools(mcp=mcp, tools=tool_mapper.tools, consumer=consumer)



def run()->None:
    ...