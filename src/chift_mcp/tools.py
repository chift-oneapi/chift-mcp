from typing import Annotated, Any

import chift

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context
from fastmcp.tools import Tool
from fastmcp.tools.tool_transform import ArgTransform, forward
from fastmcp.utilities.logging import get_logger
from pydantic import Field

from chift_mcp.utils.tool_factory import ToolFactory

logger = get_logger(__name__)


class HideConsumerIdToolFactory(ToolFactory):
    def __init__(self):
        self.consumer_id = None

    async def transform_fn(self, **kwargs):
        self.consumer_id = get_context().get_state("consumer_id")
        return await forward(**kwargs)

    def _customize_tool(self, tool: Tool) -> Tool | None:
        return tool.from_tool(
            tool=tool,
            transform_args={
                "consumer_id": ArgTransform(hide=True, default_factory=lambda: self.consumer_id)
            },
            transform_fn=self.transform_fn,
        )


class PaginationToolFactory(ToolFactory):
    def __init__(self):
        self.page = 1
        self.size = 100
        self.count = 0

    async def transform_fn(
        self,
        limit: Annotated[
            int, Field(ge=1, le=100, description="The number of items to return")
        ] = 50,
        **kwargs,
    ):
        all_items = []
        async for page in self._iter_pages(limit=limit, **kwargs):
            all_items.extend(page)
        return all_items

    async def _iter_pages(self, limit: int, **kwargs):
        self.size = limit if limit and limit < 100 else 100
        self.page = 1
        self.count = 0
        while True:
            response = await forward(**kwargs)
            structured_content = response.structured_content
            if structured_content:
                items = structured_content.get("items", [])
                yield items
                self.page += 1
                self.count += len(items)
                self.total = structured_content.get("total", 0)
                if (self.count >= self.total or not items) or (limit and self.count >= limit):
                    break

    def _convert_output_schema(self, output_schema: dict[str, Any] | None):
        if not output_schema:
            return None

        properties = output_schema.get("properties", {})
        items = properties.get("items", {})
        defs = output_schema.get("$defs", {})
        if not items:
            raise ValueError("Cannot build the new output schema.")

        new_schema = {
            "type": "object",
            "properties": {"result": items},
            "required": ["result"],
            "x-fastmcp-wrap-result": True,
        }

        if defs:
            new_schema["$defs"] = defs
        return new_schema

    def _customize_tool(self, tool: Tool) -> Tool | None:
        return Tool.from_tool(
            tool=tool,
            transform_args={
                "page": ArgTransform(hide=True, default_factory=lambda: self.page),
                "size": ArgTransform(hide=True, default_factory=lambda: self.size),
            },
            transform_fn=self.transform_fn,
            output_schema=self._convert_output_schema(tool.output_schema),
        )


def register_consumer_tools(mcp: FastMCP):
    """Register MCP tools for consumers and connections."""

    @mcp.tool()
    def consumers():
        """Get list of available consumers."""
        return chift.Consumer.all()

    @mcp.tool()
    def get_consumer(consumer_id: str):
        """Get specific consumer by ID."""
        return chift.Consumer.get(chift_id=consumer_id)

    @mcp.tool()
    def consumer_connections(consumer_id: str):
        """Get list of connections for a specific consumer."""
        consumer = chift.Consumer.get(chift_id=consumer_id)
        return consumer.Connection.all()

    return [consumers, get_consumer, consumer_connections]


async def customize_tools(mcp: FastMCP, consumer_id: str | None = None, is_remote: bool = False):
    tools = await mcp.get_tools()
    for tool_name, tool in tools.items():
        if (consumer_id or is_remote) and "consumer_id" in tool.parameters.get("properties", {}):
            tool = HideConsumerIdToolFactory.execute(tool)

        if "page" in tool.parameters.get("properties", {}) and "size" in tool.parameters.get(
            "properties", {}
        ):
            tool = PaginationToolFactory.execute(tool)

        mcp.remove_tool(tool_name)
        mcp.add_tool(tool)
