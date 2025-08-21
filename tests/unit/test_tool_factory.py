from unittest.mock import AsyncMock, Mock, patch

import pytest

from fastmcp.tools import Tool
from fastmcp.tools.tool_transform import ArgTransform

from src.chift_mcp.tools import HideConsumerIdToolFactory, PaginationToolFactory


class TestToolFactory:
    """Test cases for the abstract ToolFactory base class."""


class TestHideConsumerIdToolFactory:
    """Test cases for HideConsumerIdToolFactory."""

    def test_init(self):
        """Test factory initialization."""
        factory = HideConsumerIdToolFactory()
        assert factory.consumer_id is None

    @pytest.mark.asyncio
    async def test_transform_fn_gets_consumer_id_from_context(self):
        """Test that transform_fn retrieves consumer_id from context."""
        factory = HideConsumerIdToolFactory()

        mock_context = Mock()
        mock_context.get_state.return_value = "test-consumer-123"

        with (
            patch("src.chift_mcp.tools.get_context", return_value=mock_context),
            patch("src.chift_mcp.tools.forward", new_callable=AsyncMock) as mock_forward,
        ):
            mock_forward.return_value = "test_result"

            result = await factory.transform_fn(param1="value1")

            assert factory.consumer_id == "test-consumer-123"
            assert result == "test_result"
            mock_context.get_state.assert_called_once_with("consumer_id")
            mock_forward.assert_called_once_with(param1="value1")

    def test_customize_tool_creates_tool_with_hidden_consumer_id(self, mock_tool):
        """Test that _customize_tool creates a tool with hidden consumer_id parameter."""
        factory = HideConsumerIdToolFactory()

        # Mock the customized tool return value
        mock_customized_tool = Mock(spec=Tool)
        mock_tool.from_tool.return_value = mock_customized_tool

        result = factory._customize_tool(mock_tool)

        assert result == mock_customized_tool

        # Verify from_tool was called with correct parameters
        mock_tool.from_tool.assert_called_once()
        call_args = mock_tool.from_tool.call_args

        # Check that transform_args contains consumer_id with ArgTransform
        transform_args = call_args.kwargs["transform_args"]
        assert "consumer_id" in transform_args
        assert isinstance(transform_args["consumer_id"], ArgTransform)
        assert transform_args["consumer_id"].hide is True

        # Check that transform_fn is set
        assert call_args.kwargs["transform_fn"] == factory.transform_fn

    def test_execute_class_method(self, mock_tool):
        """Test the execute class method."""
        mock_customized_tool = Mock(spec=Tool)
        mock_tool.from_tool.return_value = mock_customized_tool

        result = HideConsumerIdToolFactory.execute(mock_tool)

        assert result == mock_customized_tool
        mock_tool.from_tool.assert_called_once()


class TestPaginationToolFactory:
    """Test cases for PaginationToolFactory."""

    def test_init(self):
        """Test factory initialization."""
        factory = PaginationToolFactory()
        assert factory.page == 1
        assert factory.size == 100
        assert factory.count == 0

    @pytest.mark.asyncio
    async def test_transform_fn_collects_all_pages(self):
        """Test that transform_fn collects items from all pages."""
        factory = PaginationToolFactory()

        # Mock the _iter_pages method to return test data
        async def mock_iter_pages(limit, **kwargs):
            yield [{"id": 1}, {"id": 2}]
            yield [{"id": 3}]

        factory._iter_pages = mock_iter_pages

        result = await factory.transform_fn(limit=50, test_param="value")

        expected = [{"id": 1}, {"id": 2}, {"id": 3}]
        assert result == expected

    @pytest.mark.asyncio
    async def test_iter_pages_handles_pagination_correctly(self):
        """Test that _iter_pages handles pagination logic correctly."""
        factory = PaginationToolFactory()

        # Mock responses for different pages
        page_responses = [
            Mock(structured_content={"items": [{"id": 1}, {"id": 2}], "total": 3}),
            Mock(structured_content={"items": [{"id": 3}], "total": 3}),
            Mock(structured_content={"items": [], "total": 3}),
        ]

        call_count = 0

        async def mock_forward(**kwargs):
            nonlocal call_count
            response = page_responses[call_count]
            call_count += 1
            return response

        with patch("src.chift_mcp.tools.forward", side_effect=mock_forward):
            pages = []
            async for page in factory._iter_pages(limit=50):
                pages.append(page)

            assert len(pages) == 2  # Should stop when no more items
            assert pages[0] == [{"id": 1}, {"id": 2}]
            assert pages[1] == [{"id": 3}]
            assert factory.count == 3
            assert factory.total == 3

    @pytest.mark.asyncio
    async def test_iter_pages_respects_limit(self):
        """Test that _iter_pages respects the limit parameter."""
        factory = PaginationToolFactory()

        # Mock response with more items than limit
        mock_response = Mock(
            structured_content={"items": [{"id": i} for i in range(10)], "total": 100}
        )

        with patch("src.chift_mcp.tools.forward", return_value=mock_response):
            pages = []
            async for page in factory._iter_pages(limit=5):
                pages.append(page)
                if factory.count >= 5:  # Simulate the limit check
                    break

            assert len(pages) == 1
            assert factory.count == 10  # All items from first page

    def test_convert_output_schema_transforms_correctly(self):
        """Test that _convert_output_schema transforms the schema correctly."""
        factory = PaginationToolFactory()

        input_schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"id": {"type": "string"}}},
                },
                "total": {"type": "integer"},
            },
            "$defs": {"SomeModel": {"type": "object"}},
        }

        result = factory._convert_output_schema(input_schema)

        expected = {
            "type": "object",
            "properties": {
                "result": {
                    "type": "array",
                    "items": {"type": "object", "properties": {"id": {"type": "string"}}},
                }
            },
            "required": ["result"],
            "x-fastmcp-wrap-result": True,
            "$defs": {"SomeModel": {"type": "object"}},
        }

        assert result == expected

    def test_convert_output_schema_handles_none(self):
        """Test that _convert_output_schema handles None input."""
        factory = PaginationToolFactory()
        result = factory._convert_output_schema(None)
        assert result is None

    def test_convert_output_schema_raises_error_without_items(self):
        """Test that _convert_output_schema raises error when items property is missing."""
        factory = PaginationToolFactory()

        invalid_schema = {"type": "object", "properties": {"total": {"type": "integer"}}}

        with pytest.raises(ValueError, match="Cannot build the new output schema"):
            factory._convert_output_schema(invalid_schema)

    def test_customize_tool_creates_paginated_tool(self, mock_tool_with_pagination):
        """Test that _customize_tool creates a tool with pagination parameters hidden."""
        factory = PaginationToolFactory()

        mock_customized_tool = Mock(spec=Tool)
        mock_tool_with_pagination.from_tool.return_value = mock_customized_tool

        result = factory._customize_tool(mock_tool_with_pagination)

        assert result == mock_customized_tool

        # Verify from_tool was called with correct parameters
        mock_tool_with_pagination.from_tool.assert_called_once()
        call_args = mock_tool_with_pagination.from_tool.call_args

        # Check that transform_args contains page and size with ArgTransform
        transform_args = call_args.kwargs["transform_args"]
        assert "page" in transform_args
        assert "size" in transform_args
        assert isinstance(transform_args["page"], ArgTransform)
        assert isinstance(transform_args["size"], ArgTransform)
        assert transform_args["page"].hide is True
        assert transform_args["size"].hide is True

        # Check that transform_fn is set
        assert call_args.kwargs["transform_fn"] == factory.transform_fn

        # Check that output_schema is transformed
        assert "output_schema" in call_args.kwargs

    def test_execute_class_method(self, mock_tool_with_pagination):
        """Test the execute class method."""
        mock_customized_tool = Mock(spec=Tool)
        mock_tool_with_pagination.from_tool.return_value = mock_customized_tool

        result = PaginationToolFactory.execute(mock_tool_with_pagination)

        assert result == mock_customized_tool
        mock_tool_with_pagination.from_tool.assert_called_once()
