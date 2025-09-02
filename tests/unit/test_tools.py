from unittest.mock import AsyncMock, Mock, patch

import pytest

from fastmcp.tools import Tool

from src.chift_mcp.tools import (
    customize_tools,
)


class TestRegisterConsumerTools:
    """Test cases for register_consumer_tools function."""


class TestCustomizeTools:
    """Test cases for customize_tools function."""

    @pytest.mark.asyncio
    async def test_customize_tools_no_customization_needed(self, mock_fastmcp):
        """Test customize_tools when no customization is needed."""
        # Mock tools without consumer_id, page, or size parameters
        mock_tool1 = Mock(spec=Tool)
        mock_tool1.parameters = {"properties": {"name": {"type": "string"}}}
        mock_tool2 = Mock(spec=Tool)
        mock_tool2.parameters = {"properties": {"id": {"type": "integer"}}}

        mock_tools = {"tool1": mock_tool1, "tool2": mock_tool2}
        mock_fastmcp.get_tools = AsyncMock(return_value=mock_tools)

        await customize_tools(mock_fastmcp)

        # Verify tools were removed and re-added (even without customization)
        assert mock_fastmcp.remove_tool.call_count == 2
        assert mock_fastmcp.add_tool.call_count == 2

        mock_fastmcp.remove_tool.assert_any_call("tool1")
        mock_fastmcp.remove_tool.assert_any_call("tool2")
        mock_fastmcp.add_tool.assert_any_call(mock_tool1)
        mock_fastmcp.add_tool.assert_any_call(mock_tool2)

    @pytest.mark.asyncio
    async def test_customize_tools_hides_consumer_id_when_consumer_id_provided(
        self, mock_fastmcp, mock_tool_with_consumer_id
    ):
        """Test customize_tools hides consumer_id parameter when consumer_id is provided."""
        mock_tools = {"test_tool": mock_tool_with_consumer_id}
        mock_fastmcp.get_tools = AsyncMock(return_value=mock_tools)

        # Mock HideConsumerIdToolFactory
        mock_customized_tool = Mock(spec=Tool)
        mock_customized_tool.parameters = {
            "properties": {"name": {"type": "string"}}  # consumer_id should be hidden
        }
        with patch("src.chift_mcp.tools.HideConsumerIdToolFactory") as mock_factory_class:
            mock_factory_class.execute.return_value = mock_customized_tool

            await customize_tools(mock_fastmcp, consumer_id="test-consumer-id")

            # Verify factory was used
            mock_factory_class.execute.assert_called_once_with(mock_tool_with_consumer_id)

            # Verify tool was replaced
            mock_fastmcp.remove_tool.assert_called_once_with("test_tool")
            mock_fastmcp.add_tool.assert_called_once_with(mock_customized_tool)

    @pytest.mark.asyncio
    async def test_customize_tools_hides_consumer_id_when_is_remote_true(
        self, mock_fastmcp, mock_tool_with_consumer_id
    ):
        """Test customize_tools hides consumer_id parameter when is_remote is True."""
        mock_tools = {"test_tool": mock_tool_with_consumer_id}
        mock_fastmcp.get_tools = AsyncMock(return_value=mock_tools)

        # Mock HideConsumerIdToolFactory
        mock_customized_tool = Mock(spec=Tool)
        mock_customized_tool.parameters = {
            "properties": {"name": {"type": "string"}}  # consumer_id should be hidden
        }
        with patch("src.chift_mcp.tools.HideConsumerIdToolFactory") as mock_factory_class:
            mock_factory_class.execute.return_value = mock_customized_tool

            await customize_tools(mock_fastmcp, consumer_id=None, is_remote=True)

            # Verify factory was used
            mock_factory_class.execute.assert_called_once_with(mock_tool_with_consumer_id)

            # Verify tool was replaced
            mock_fastmcp.remove_tool.assert_called_once_with("test_tool")
            mock_fastmcp.add_tool.assert_called_once_with(mock_customized_tool)

    @pytest.mark.asyncio
    async def test_customize_tools_adds_pagination_for_page_size_params(
        self, mock_fastmcp, mock_tool_with_pagination
    ):
        """Test customize_tools adds pagination for tools with page and size parameters."""
        mock_tools = {"paginated_tool": mock_tool_with_pagination}
        mock_fastmcp.get_tools = AsyncMock(return_value=mock_tools)

        # Mock PaginationToolFactory
        mock_customized_tool = Mock(spec=Tool)
        with patch("src.chift_mcp.tools.PaginationToolFactory") as mock_factory_class:
            mock_factory_class.execute.return_value = mock_customized_tool

            await customize_tools(mock_fastmcp)

            # Verify factory was used
            mock_factory_class.execute.assert_called_once_with(mock_tool_with_pagination)

            # Verify tool was replaced
            mock_fastmcp.remove_tool.assert_called_once_with("paginated_tool")
            mock_fastmcp.add_tool.assert_called_once_with(mock_customized_tool)

    @pytest.mark.asyncio
    async def test_customize_tools_applies_both_customizations(
        self, mock_fastmcp, mock_tool_with_consumer_id_and_pagination
    ):
        """Test customize_tools applies both consumer_id hiding and pagination."""
        mock_tools = {"complex_tool": mock_tool_with_consumer_id_and_pagination}
        mock_fastmcp.get_tools = AsyncMock(return_value=mock_tools)

        # Mock both factories
        mock_hide_customized_tool = Mock(spec=Tool)
        mock_hide_customized_tool.parameters = {
            "properties": {
                "page": {"type": "integer"},
                "size": {"type": "integer"},
                "name": {"type": "string"},
            }
        }
        mock_pagination_customized_tool = Mock(spec=Tool)

        with (
            patch("src.chift_mcp.tools.HideConsumerIdToolFactory") as mock_hide_factory,
            patch("src.chift_mcp.tools.PaginationToolFactory") as mock_pagination_factory,
        ):
            mock_hide_factory.execute.return_value = mock_hide_customized_tool
            mock_pagination_factory.execute.return_value = mock_pagination_customized_tool

            await customize_tools(mock_fastmcp, consumer_id="test-consumer-id")

            # Verify both factories were used in sequence
            mock_hide_factory.execute.assert_called_once_with(
                mock_tool_with_consumer_id_and_pagination
            )
            mock_pagination_factory.execute.assert_called_once_with(mock_hide_customized_tool)

            # Verify final tool was used
            mock_fastmcp.remove_tool.assert_called_once_with("complex_tool")
            mock_fastmcp.add_tool.assert_called_once_with(mock_pagination_customized_tool)

    @pytest.mark.asyncio
    async def test_customize_tools_handles_empty_tools_dict(self, mock_fastmcp):
        """Test customize_tools handles empty tools dictionary."""
        mock_fastmcp.get_tools = AsyncMock(return_value={})

        await customize_tools(mock_fastmcp)

        # Should not call remove_tool or add_tool
        mock_fastmcp.remove_tool.assert_not_called()
        mock_fastmcp.add_tool.assert_not_called()

    @pytest.mark.asyncio
    async def test_customize_tools_preserves_tool_order(self, mock_fastmcp):
        """Test that customize_tools preserves the order of tool processing."""
        # Mock multiple tools
        mock_tool1 = Mock(spec=Tool)
        mock_tool1.parameters = {"properties": {"name": {"type": "string"}}}
        mock_tool2 = Mock(spec=Tool)
        mock_tool2.parameters = {"properties": {"id": {"type": "integer"}}}
        mock_tool3 = Mock(spec=Tool)
        mock_tool3.parameters = {"properties": {"value": {"type": "number"}}}

        # Use OrderedDict to ensure order
        from collections import OrderedDict

        mock_tools = OrderedDict(
            [("tool1", mock_tool1), ("tool2", mock_tool2), ("tool3", mock_tool3)]
        )
        mock_fastmcp.get_tools = AsyncMock(return_value=mock_tools)

        await customize_tools(mock_fastmcp)

        assert mock_fastmcp.remove_tool.call_count == 3
        assert mock_fastmcp.add_tool.call_count == 3
