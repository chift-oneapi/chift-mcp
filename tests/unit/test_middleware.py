from unittest.mock import AsyncMock, Mock, patch

import pytest

from fastmcp.tools.tool import Tool

from src.chift_mcp.middleware import FilterToolsMiddleware, UserAuthMiddleware


class TestUserAuthMiddleware:
    """Test cases for UserAuthMiddleware."""

    @pytest.mark.asyncio
    async def test_on_request_with_no_consumer_id(self, mock_middleware_context):
        """Test on_request when no consumer_id is set."""
        middleware = UserAuthMiddleware()

        # Mock call_next
        mock_call_next = AsyncMock()
        mock_call_next.return_value = "test_result"

        result = await middleware.on_request(mock_middleware_context, mock_call_next)

        assert result == "test_result"
        mock_call_next.assert_called_once_with(mock_middleware_context)

    @pytest.mark.asyncio
    async def test_on_request_with_consumer_id_sets_state(
        self, mock_middleware_context, mock_fastmcp_context
    ):
        """Test on_request sets consumer_id in context state."""
        middleware = UserAuthMiddleware(env_consumer_id="test-consumer-456")

        # Set up the middleware context with fastmcp_context
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        mock_call_next = AsyncMock()
        mock_call_next.return_value = "test_result"

        result = await middleware.on_request(mock_middleware_context, mock_call_next)

        assert result == "test_result"
        mock_fastmcp_context.set_state.assert_called_once_with("consumer_id", "test-consumer-456")
        mock_call_next.assert_called_once_with(mock_middleware_context)

    @pytest.mark.asyncio
    async def test_on_request_raises_error_when_no_fastmcp_context(self, mock_middleware_context):
        """Test on_request raises error when fastmcp_context is None."""
        middleware = UserAuthMiddleware(env_consumer_id="test-consumer-789")

        mock_middleware_context.fastmcp_context = None

        mock_call_next = AsyncMock()

        with pytest.raises(ValueError, match="FastMCP context is not set"):
            await middleware.on_request(mock_middleware_context, mock_call_next)


class TestFilterToolsMiddleware:
    """Test cases for FilterToolsMiddleware."""

    def test_init(self):
        """Test middleware initialization."""
        middleware = FilterToolsMiddleware()
        # No specific initialization to test, just ensure it doesn't error
        assert middleware is not None

    def test_connection_types_without_consumer_id(self):
        """Test connection_types method returns all types when no consumer_id."""
        middleware = FilterToolsMiddleware()

        result = middleware.connection_types(None)

        expected = [
            "accounting",
            "pos",
            "ecommerce",
            "invoicing",
            "banking",
            "payment",
            "pms",
            "custom",
        ]
        assert result == expected

    @patch("src.chift_mcp.middleware.chift")
    def test_connection_types_with_consumer_id(self, mock_chift):
        """Test connection_types method returns specific types for consumer."""
        middleware = FilterToolsMiddleware()

        # Mock consumer and connections
        mock_consumer = Mock()
        mock_connection1 = Mock()
        mock_connection1.api = "Accounting"
        mock_connection2 = Mock()
        mock_connection2.api = "Point of Sale"

        mock_consumer.Connection.all.return_value = [mock_connection1, mock_connection2]
        mock_chift.Consumer.get.return_value = mock_consumer

        result = middleware.connection_types("test-consumer-id")

        expected = ["accounting", "pos"]
        assert result == expected
        mock_chift.Consumer.get.assert_called_once_with(chift_id="test-consumer-id")
        mock_consumer.Connection.all.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_list_tools_no_consumer_id_in_context(
        self, mock_middleware_context, mock_fastmcp_context
    ):
        """Test on_list_tools when no consumer_id in context."""
        middleware = FilterToolsMiddleware()

        # Set up context
        mock_fastmcp_context.get_state.return_value = None
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        # Mock call_next
        mock_tools = [Mock(spec=Tool), Mock(spec=Tool)]
        mock_call_next = AsyncMock()
        mock_call_next.return_value = mock_tools

        result = await middleware.on_list_tools(mock_middleware_context, mock_call_next)

        assert result == mock_tools
        mock_fastmcp_context.get_state.assert_called_once_with("consumer_id")
        mock_call_next.assert_called_once_with(mock_middleware_context)

    @pytest.mark.asyncio
    async def test_on_list_tools_filters_by_connection_types(
        self, mock_middleware_context, mock_fastmcp_context
    ):
        """Test on_list_tools filters tools by connection types."""
        middleware = FilterToolsMiddleware()

        # Mock context with consumer_id
        mock_fastmcp_context.get_state.return_value = "test-consumer-id"
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        # Mock tools with different tags
        mock_tool1 = Mock(spec=Tool)
        mock_tool1.tags = ["accounting", "other"]
        mock_tool2 = Mock(spec=Tool)
        mock_tool2.tags = ["pos"]
        mock_tool3 = Mock(spec=Tool)
        mock_tool3.tags = ["ecommerce"]  # This should be filtered out
        mock_tool4 = Mock(spec=Tool)
        mock_tool4.tags = None  # This should be filtered out

        mock_tools = [mock_tool1, mock_tool2, mock_tool3, mock_tool4]
        mock_call_next = AsyncMock()
        mock_call_next.return_value = mock_tools

        # Mock connection_types method
        middleware.connection_types = Mock(return_value=["accounting", "pos"])

        result = await middleware.on_list_tools(mock_middleware_context, mock_call_next)

        # Should only include tools with matching tags
        assert len(result) == 2
        assert mock_tool1 in result
        assert mock_tool2 in result
        assert mock_tool3 not in result
        assert mock_tool4 not in result

        middleware.connection_types.assert_called_once_with("test-consumer-id")
        mock_call_next.assert_called_once_with(mock_middleware_context)

    @pytest.mark.asyncio
    async def test_on_list_tools_raises_error_when_no_fastmcp_context(
        self, mock_middleware_context
    ):
        """Test on_list_tools raises error when fastmcp_context is None."""
        middleware = FilterToolsMiddleware()

        mock_middleware_context.fastmcp_context = None

        mock_call_next = AsyncMock()

        with pytest.raises(ValueError, match="FastMCP context is not set"):
            await middleware.on_list_tools(mock_middleware_context, mock_call_next)

    @pytest.mark.asyncio
    async def test_on_list_tools_handles_tools_without_tags(
        self, mock_middleware_context, mock_fastmcp_context
    ):
        """Test on_list_tools correctly handles tools without tags."""
        middleware = FilterToolsMiddleware()

        # Mock context with consumer_id
        mock_fastmcp_context.get_state.return_value = "test-consumer-id"
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        # Mock tools, some without tags
        mock_tool1 = Mock(spec=Tool)
        mock_tool1.tags = ["accounting"]
        mock_tool2 = Mock(spec=Tool)
        mock_tool2.tags = None
        mock_tool3 = Mock(spec=Tool)
        mock_tool3.tags = []

        mock_tools = [mock_tool1, mock_tool2, mock_tool3]
        mock_call_next = AsyncMock()
        mock_call_next.return_value = mock_tools

        # Mock connection_types method
        middleware.connection_types = Mock(return_value=["accounting"])

        result = await middleware.on_list_tools(mock_middleware_context, mock_call_next)

        # Should only include tool with matching tags
        assert len(result) == 1
        assert mock_tool1 in result
        assert mock_tool2 not in result
        assert mock_tool3 not in result
