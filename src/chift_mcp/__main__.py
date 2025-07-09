import textwrap

import chift

from chift.openapi.openapi import ConsumerItem
from mcp.server import FastMCP

from chift_mcp.config import (
    Chift as ChiftConfig,
    config,
)
from chift_mcp.utils.importer import import_toolkit_functions


def configure_chift(chift_config: ChiftConfig) -> None:
    """Configure global Chift client settings."""
    chift.client_secret = chift_config.client_secret
    chift.client_id = chift_config.client_id
    chift.account_id = chift_config.account_id
    chift.url_base = chift_config.url_base


def create_mcp_server(name: str) -> FastMCP:
    """Initialize and configure the MCP server with prompt."""
    mcp = FastMCP(name)

    @mcp.prompt()
    def initial_prompt() -> str:
        return textwrap.dedent(
            """
                        You are an AI assistant for the Chift API using MCP server tools.
            
                        1. First, use the 'consumers' tool to get available consumers.
                        2. Display this list and REQUIRE explicit selection:
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
        )

    return mcp


def register_tools(mcp: FastMCP):
    """Register MCP tools for consumers and connections."""

    @mcp.tool()
    def consumers() -> list[ConsumerItem]:
        """Get list of available consumers."""
        return chift.Consumer.all()

    @mcp.tool()
    def get_consumer(consumer_id: str) -> ConsumerItem:
        """Get specific consumer by ID."""
        return chift.Consumer.get(chift_id=consumer_id)

    @mcp.tool()
    def consumer_connections(consumer_id: str):
        """Get list of connections for a specific consumer."""
        consumer = chift.Consumer.get(chift_id=consumer_id)
        return consumer.Connection.all()


def main() -> None:
    configure_chift(config.chift)
    mcp = create_mcp_server("Chift API Bridge")
    register_tools(mcp)
    import_toolkit_functions(config=config.chift.function_config, mcp=mcp)
    mcp.run()


if __name__ == "__main__":
    main()
