from typing import Any

import chift
import mcp.types as mt

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import Tool
from fastmcp.utilities.logging import get_logger

from chift_mcp.utils.utils import CONNECTION_TYPES

logger = get_logger(__name__)


class UserAuthMiddleware(Middleware):
    """
    Middleware to authenticate the user.
    """

    def __init__(self, env_consumer_id: str | None = None):
        self.consumer_id = env_consumer_id

    async def on_request(
        self,
        context: MiddlewareContext[mt.Request],
        call_next: CallNext[mt.Request, Any],
    ) -> Any:
        if self.consumer_id is None:
            return await call_next(context)

        if context.fastmcp_context is None:
            raise ValueError("FastMCP context is not set")

        context.fastmcp_context.set_state("consumer_id", self.consumer_id)

        return await call_next(context)


class FilterToolsMiddleware(Middleware):
    """
    Filter tools based on the consumer ID. Only returns the tools that are
    available for the required consumer.
    """

    def connection_types(self, consumer_id: str | None) -> list[str]:
        """
        Get the connection types for a consumer.

        Args:
            consumer_id (str): The consumer ID

        Returns:
            list[str]: The connection types
        """
        if consumer_id is None:
            return list(CONNECTION_TYPES.values())

        consumer = chift.Consumer.get(chift_id=consumer_id)
        connections = consumer.Connection.all()
        return [CONNECTION_TYPES[connection.api] for connection in connections]

    async def on_list_tools(
        self,
        context: MiddlewareContext[mt.ListToolsRequest],
        call_next: CallNext[mt.ListToolsRequest, list[Tool]],
    ) -> list[Tool]:
        if context.fastmcp_context is None:
            raise ValueError("FastMCP context is not set")

        consumer_id = context.fastmcp_context.get_state("consumer_id")

        if consumer_id is None:
            return await call_next(context)

        result = await call_next(context)
        connection_types = self.connection_types(consumer_id)
        result = [
            tool
            for tool in result
            if tool.tags and any(tag in connection_types for tag in tool.tags)
        ]

        return result
