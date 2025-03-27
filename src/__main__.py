import chift
from mcp.server import FastMCP

from src.config import config
from src.utils.importer import import_toolkit_functions

chift.client_secret = config.chift.client_secret
chift.client_id = config.chift.client_id
chift.account_id = config.chift.account_id
chift.url_base = config.chift.url_base


mcp = FastMCP("Chift API Bridge")


@mcp.prompt()
def initial_prompt() -> str:
    return """
        You are an AI assistant for the Chift API using MCP server tools.

        1. First, use the 'consumers' tool to get available consumers.

        2. Display this list to the user and REQUIRE explicit selection:
           - Specific consumer ID(s)/name(s)
           - OR explicit confirmation to use ALL consumers
           - DO NOT proceed without clear selection

        3. For each selected consumer, use 'get_consumer' for details.

        4. Use 'consumer_connections' to get available endpoints.

        5. Only use endpoints available for the selected consumer(s).

        6. Format responses as:

        <response>
        Your response to the user.
        </response>

        <api_interaction>
        API call details and results.
        </api_interaction>
"""


@mcp.tool()
def consumers() -> list[chift.Consumer]:
    """Get list of available consumers"""
    return chift.Consumer.all()


@mcp.tool()
def get_consumer(consumer_id: str) -> chift.Consumer:
    """Get specific consumer"""
    return chift.Consumer.get(chift_id=consumer_id)


@mcp.tool()
def consumer_connections(consumer_id: str):
    """Get list of connections for a specific consumer"""
    _consumer = chift.Consumer.get(chift_id=consumer_id)
    return _consumer.Connection.all()


import_toolkit_functions(config=config.chift.function_config, mcp=mcp)



def run()->None:
    mcp.run()
