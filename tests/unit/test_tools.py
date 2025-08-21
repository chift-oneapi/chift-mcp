from unittest.mock import AsyncMock, Mock, patch

import pytest

from fastmcp import FastMCP
from fastmcp.tools import Tool

from src.chift_mcp.tools import (
    customize_tools,
    register_consumer_tools,
)


class TestRegisterConsumerTools:
    """Test cases for register_consumer_tools function."""

    @patch("src.chift_mcp.tools.chift")
    def test_register_consumer_tools_registers_all_tools(self, mock_chift, dummy_mcp):
        """Test that register_consumer_tools registers all expected tools."""
        registered_tools = []

        def mock_tool_decorator():
            def decorator(func):
                registered_tools.append(func)
                return func

            return decorator

        dummy_mcp.tool = mock_tool_decorator

        # Mock chift responses
        mock_consumers = [{"id": "consumer1"}, {"id": "consumer2"}]
        mock_consumer = Mock()
        mock_connections = [{"id": "conn1"}, {"id": "conn2"}]

        mock_chift.Consumer.all.return_value = mock_consumers
        mock_chift.Consumer.get.return_value = mock_consumer
        mock_consumer.Connection.all.return_value = mock_connections

        # Call the function
        result = register_consumer_tools(dummy_mcp)

        # Verify tools were registered
        assert len(registered_tools) == 3
        assert result == registered_tools

        # Test each registered tool
        consumers_func = registered_tools[0]
        assert consumers_func.__name__ == "consumers"
        assert "Get list of available consumers" in consumers_func.__doc__

        get_consumer_func = registered_tools[1]
        assert get_consumer_func.__name__ == "get_consumer"
        assert "Get specific consumer by ID" in get_consumer_func.__doc__

        consumer_connections_func = registered_tools[2]
        assert consumer_connections_func.__name__ == "consumer_connections"
        assert (
            "Get list of connections for a specific consumer" in consumer_connections_func.__doc__
        )

    @patch("src.chift_mcp.tools.chift")
    def test_consumers_tool_calls_chift_api(self, mock_chift, dummy_mcp):
        """Test that the consumers tool calls the correct chift API."""
        registered_tools = []

        def mock_tool_decorator():
            def decorator(func):
                registered_tools.append(func)
                return func

            return decorator

        dummy_mcp.tool = mock_tool_decorator

        expected_consumers = [{"id": "consumer1"}, {"id": "consumer2"}]
        mock_chift.Consumer.all.return_value = expected_consumers

        register_consumer_tools(dummy_mcp)

        # Test the consumers function
        consumers_func = registered_tools[0]
        result = consumers_func()

        assert result == expected_consumers
        mock_chift.Consumer.all.assert_called_once()

    @patch("src.chift_mcp.tools.chift")
    def test_get_consumer_tool_calls_chift_api(self, mock_chift, dummy_mcp):
        """Test that the get_consumer tool calls the correct chift API."""
        registered_tools = []

        def mock_tool_decorator():
            def decorator(func):
                registered_tools.append(func)
                return func

            return decorator

        dummy_mcp.tool = mock_tool_decorator

        expected_consumer = {"id": "consumer1", "name": "Test Consumer"}
        mock_chift.Consumer.get.return_value = expected_consumer

        register_consumer_tools(dummy_mcp)

        # Test the get_consumer function
        get_consumer_func = registered_tools[1]
        result = get_consumer_func("test-consumer-id")

        assert result == expected_consumer
        mock_chift.Consumer.get.assert_called_once_with(chift_id="test-consumer-id")

    @patch("src.chift_mcp.tools.chift")
    def test_consumer_connections_tool_calls_chift_api(self, mock_chift, dummy_mcp):
        """Test that the consumer_connections tool calls the correct chift API."""
        registered_tools = []

        def mock_tool_decorator():
            def decorator(func):
                registered_tools.append(func)
                return func

            return decorator

        dummy_mcp.tool = mock_tool_decorator

        mock_consumer = Mock()
        expected_connections = [{"id": "conn1"}, {"id": "conn2"}]
        mock_consumer.Connection.all.return_value = expected_connections
        mock_chift.Consumer.get.return_value = mock_consumer

        register_consumer_tools(dummy_mcp)

        # Test the consumer_connections function
        consumer_connections_func = registered_tools[2]
        result = consumer_connections_func("test-consumer-id")

        assert result == expected_connections
        mock_chift.Consumer.get.assert_called_once_with(chift_id="test-consumer-id")
        mock_consumer.Connection.all.assert_called_once()


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
