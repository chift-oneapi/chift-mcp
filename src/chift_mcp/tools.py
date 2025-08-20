from typing import Annotated

import chift

from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.tools.tool_transform import ArgTransform, forward
from fastmcp.utilities.logging import get_logger
from fastmcp.utilities.types import NotSet
from pydantic import Field

logger = get_logger(__name__)

class ToolCustomizer:
    def __init__(self, tool: Tool, consumer_id: str | None = None):
        self.page = 1
        self.size = 100
        self.count = 0
        self.tool = tool
        self.consumer_id = consumer_id

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

    async def pagination_response(
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

    def get_arg_transform(self):
        return {
            "page": ArgTransform(hide=True, default_factory=lambda: self.page),
            "size": ArgTransform(hide=True, default_factory=lambda: self.size),
        }

    def customize_tool(self):
        properties = self.tool.parameters.get("properties", {})
        original_output_schema = self.tool.output_schema

        transform_args: dict[str, ArgTransform] = {}
        should_paginate = False
        output_schema = None
        change_consumer_id = False

        if self.consumer_id and "consumer_id" in properties:
            change_consumer_id = True
            transform_args["consumer_id"] = ArgTransform(hide=True, default=self.consumer_id)

        if "page" in properties and "size" in properties:
            transform_args.update(self.get_arg_transform())
            should_paginate = True
            if original_output_schema:  # TODO make better
                schema_properties = original_output_schema.get("properties", {})
                items = schema_properties.get("items", {})
                output_schema = items
                logger.info(f"output_schema: {output_schema}")

        if change_consumer_id or should_paginate:
            return self.tool.from_tool(
                tool=self.tool,
                transform_args=transform_args if change_consumer_id else None,
                transform_fn=self.pagination_response if should_paginate else None,
                output_schema=None,  # TODO correct
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


async def customize_tools(mcp: FastMCP, consumer_id: str | None = None) -> None:
    tools = await mcp.get_tools()
    logger.info(f"Available tools: {list(tools.keys())}")

    # for tool_name, tool in tools.items():
    #     new_tool = ToolCustomizer(tool, consumer_id).customize_tool()
    #     if new_tool:
    #         mcp.remove_tool(tool_name)
    #         mcp.add_tool(new_tool)