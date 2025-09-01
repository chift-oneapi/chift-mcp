from typing import Any

import chift
import mcp.types as mt

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import Tool
from fastmcp.utilities.logging import get_logger

from chift_mcp.constants import CONNECTION_TYPES

logger = get_logger(__name__)


class EnvAuthMiddleware(Middleware):
    """
    Middleware to add the consumer ID and function config to the context from the environment vars.
    For STDIO MCP only
    """

    def __init__(
        self,
        consumer_id: str | None,
        function_config: dict[str, list[str]],
    ):
        self.consumer_id = consumer_id
        self.function_config = function_config

    def connection_types(self, consumer_id: str) -> list[str]:
        """
        Get the connection types for a consumer.

        Args:
            consumer_id (str): The consumer ID

        Returns:
            list[str]: The connection types
        """

        consumer = chift.Consumer.get(chift_id=consumer_id)
        connections = consumer.Connection.all()
        return [CONNECTION_TYPES[connection.api] for connection in connections]

    async def on_request(
        self,
        context: MiddlewareContext[mt.Request],
        call_next: CallNext[mt.Request, Any],
    ) -> Any:
        if context.fastmcp_context is None:
            raise ValueError("FastMCP context is not set")

        function_config = self.function_config

        # Filter domains to only include only if consumer_id is set
        if self.consumer_id:
            context.fastmcp_context.set_state("consumer_id", self.consumer_id)
            connection_types = self.connection_types(self.consumer_id)
            function_config = {
                domain: operations
                for domain, operations in self.function_config.items()
                if domain in connection_types
            }

        context.fastmcp_context.set_state("function_config", function_config)

        return await call_next(context)


class FilterToolsMiddleware(Middleware):
    """
    Filter tools based on the consumer ID. Only returns the tools that are
    available for the required consumer.
    """

    def __init__(self, consumer_id: str | None, is_remote: bool):
        self.consumer_id = consumer_id
        self.is_remote = is_remote

    async def on_list_tools(
        self,
        context: MiddlewareContext[mt.ListToolsRequest],
        call_next: CallNext[mt.ListToolsRequest, list[Tool]],
    ) -> list[Tool]:
        if context.fastmcp_context is None:
            raise ValueError("FastMCP context is not set")

        function_config = context.fastmcp_context.get_state("function_config")
        if function_config is None:
            return await call_next(context)

        connection_types = list(function_config.keys())

        result = await call_next(context)
        filtered_tools = []
        for tool in result:
            if tool.name == "SearchChift":  # Special Tool coming from the proxy
                filtered_tools.append(tool)
                continue

            parts = tool.name.split("_")
            if len(parts) != 3:
                logger.warning(
                    f"Tool {tool.name} has invalid name, expected 3 parts got {len(parts)}"
                )
                continue
            domain = parts[0]
            operation = parts[1]
            if (
                self.consumer_id is None
                and self.is_remote is False
                and domain in ["consumers", "connections"]
                and operation == "get"
            ):
                # Add 3 special tools when consumer_id is not set and not remote
                filtered_tools.append(tool)
                continue

            if domain not in connection_types or operation not in function_config.get(domain, []):
                continue

            filtered_tools.append(tool)

        return filtered_tools
