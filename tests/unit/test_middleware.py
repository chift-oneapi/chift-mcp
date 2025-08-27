from unittest.mock import AsyncMock, Mock

import pytest

from fastmcp.tools.tool import Tool

from src.chift_mcp.middleware import FilterToolsMiddleware, EnvAuthMiddleware


class TestUserAuthMiddleware:
    """Test cases for UserAuthMiddleware."""

    @pytest.mark.asyncio
    async def test_on_request_with_no_consumer_id(self, mock_middleware_context):
        """Test on_request when no consumer_id is set."""
        function_config = {"accounting": ["mock", "create"], "pos": ["other"]}
        middleware = EnvAuthMiddleware(None, function_config)

        # Set up the middleware context with fastmcp_context
        mock_fastmcp_context = Mock()
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        # Mock call_next
        mock_call_next = AsyncMock()
        mock_call_next.return_value = "test_result"

        result = await middleware.on_request(mock_middleware_context, mock_call_next)

        assert result == "test_result"
        mock_call_next.assert_called_once_with(mock_middleware_context)
        mock_fastmcp_context.set_state.assert_any_call("function_config", function_config)

    @pytest.mark.asyncio
    async def test_on_request_with_consumer_id_sets_state(
        self, mock_middleware_context, mock_fastmcp_context
    ):
        """Test on_request sets consumer_id in context state."""
        function_config = {"accounting": ["mock"], "pos": ["other"]}
        middleware = EnvAuthMiddleware("test-consumer-456", function_config)

        # Set up the middleware context with fastmcp_context
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        # Only return accounting connections for this consumer
        middleware.connection_types = Mock(return_value=["accounting"])  # type: ignore[attr-defined]

        mock_call_next = AsyncMock()
        mock_call_next.return_value = "test_result"

        result = await middleware.on_request(mock_middleware_context, mock_call_next)

        assert result == "test_result"
        mock_fastmcp_context.set_state.assert_any_call("consumer_id", "test-consumer-456")
        mock_fastmcp_context.set_state.assert_any_call("function_config", {"accounting": ["mock"]})
        mock_call_next.assert_called_once_with(mock_middleware_context)

    @pytest.mark.asyncio
    async def test_on_request_raises_error_when_no_fastmcp_context(self, mock_middleware_context):
        """Test on_request raises error when fastmcp_context is None."""
        function_config = {"accounting": ["mock"]}
        middleware = EnvAuthMiddleware("test-consumer-789", function_config)

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
        mock_fastmcp_context.get_state.assert_called_once_with("function_config")
        mock_call_next.assert_called_once_with(mock_middleware_context)

    @pytest.mark.asyncio
    async def test_on_list_tools_filters_by_connection_types(
        self, mock_middleware_context, mock_fastmcp_context
    ):
        """Test on_list_tools filters tools by connection types."""
        middleware = FilterToolsMiddleware()

        # Mock context with function_config
        mock_fastmcp_context.get_state.return_value = {
            "accounting": ["mock"],
            "pos": ["other"],
        }
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        # Mock tools with different tags
        mock_tool1 = Mock(spec=Tool)
        mock_tool1.name = "accounting_mock_tool"
        mock_tool2 = Mock(spec=Tool)
        mock_tool2.name = "pos_other_tool"
        mock_tool3 = Mock(spec=Tool)
        mock_tool3.name = "ecommerce_mock_tool"  # This should be filtered out
        mock_tool4 = Mock(spec=Tool)
        mock_tool4.name = "ecommerce_other_tool"  # This should be filtered out

        mock_tools = [mock_tool1, mock_tool2, mock_tool3, mock_tool4]
        mock_call_next = AsyncMock()
        mock_call_next.return_value = mock_tools

        result = await middleware.on_list_tools(mock_middleware_context, mock_call_next)

        # Should only include tools with matching tags
        assert len(result) == 2
        assert mock_tool1 in result
        assert mock_tool2 in result
        assert mock_tool3 not in result
        assert mock_tool4 not in result
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
        """Test on_list_tools correctly handles tools without expected naming pattern."""
        middleware = FilterToolsMiddleware()

        # Mock context with function_config
        mock_fastmcp_context.get_state.return_value = {"accounting": ["mock"]}
        mock_middleware_context.fastmcp_context = mock_fastmcp_context

        # Mock tools, some without the expected 3-part name
        mock_tool1 = Mock(spec=Tool)
        mock_tool1.name = "accounting_mock_tool"
        mock_tool2 = Mock(spec=Tool)
        mock_tool2.name = "accounting_other_tool"
        mock_tool3 = Mock(spec=Tool)
        mock_tool3.name = "invalid"

        mock_tools = [mock_tool1, mock_tool2, mock_tool3]
        mock_call_next = AsyncMock()
        mock_call_next.return_value = mock_tools

        result = await middleware.on_list_tools(mock_middleware_context, mock_call_next)

        # Should include matching tool and pass through those without expected naming
        assert len(result) == 2
        assert mock_tool1 in result
        assert mock_tool2 not in result
        assert mock_tool3 in result
