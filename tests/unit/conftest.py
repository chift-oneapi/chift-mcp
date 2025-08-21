import pytest
from unittest.mock import Mock, AsyncMock
from fastmcp import FastMCP
from fastmcp.tools import Tool


class DummyMCP:
    def __init__(self):
        self.tools = []

    def add_tool(self, func, name=None, description=None):
        self.tools.append((func, name, description))

    def tool(self):
        def decorator(fn):
            self.tools.append(fn)
            return fn

        return decorator


@pytest.fixture
def dummy_mcp():
    return DummyMCP()


@pytest.fixture
def mock_fastmcp():
    """Create a mock FastMCP instance for testing."""
    mock_mcp = Mock(spec=FastMCP)
    mock_mcp.get_tools = AsyncMock(return_value={})
    mock_mcp.add_tool = Mock()
    mock_mcp.remove_tool = Mock()
    mock_mcp.tool = Mock()
    return mock_mcp


@pytest.fixture
def mock_tool():
    """Create a mock Tool instance for testing."""
    mock = Mock(spec=Tool)
    mock.parameters = {"properties": {}}
    mock.output_schema = None
    mock.tags = None
    mock.from_tool = Mock(return_value=mock)
    return mock


@pytest.fixture
def mock_tool_with_consumer_id():
    """Create a mock Tool with consumer_id parameter."""
    mock = Mock(spec=Tool)
    mock.parameters = {
        "properties": {"consumer_id": {"type": "string"}, "name": {"type": "string"}}
    }
    mock.output_schema = None
    mock.tags = ["accounting"]
    mock.from_tool = Mock(return_value=mock)
    return mock


@pytest.fixture
def mock_tool_with_pagination():
    """Create a mock Tool with pagination parameters."""
    mock = Mock(spec=Tool)
    mock.parameters = {
        "properties": {
            "page": {"type": "integer"},
            "size": {"type": "integer"},
            "name": {"type": "string"},
        }
    }
    mock.output_schema = {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "object"}},
            "total": {"type": "integer"},
        },
    }
    mock.tags = ["pos"]
    mock.from_tool = Mock(return_value=mock)
    return mock


@pytest.fixture
def mock_tool_with_consumer_id_and_pagination():
    """Create a mock Tool with both consumer_id and pagination parameters."""
    mock = Mock(spec=Tool)
    mock.parameters = {
        "properties": {
            "consumer_id": {"type": "string"},
            "page": {"type": "integer"},
            "size": {"type": "integer"},
            "name": {"type": "string"},
        }
    }
    mock.output_schema = {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "object"}},
            "total": {"type": "integer"},
        },
    }
    mock.tags = ["pos"]
    mock.from_tool = Mock(return_value=mock)
    return mock


@pytest.fixture
def mock_fastmcp_context():
    """Create a mock FastMCP context for middleware testing."""
    mock_context = Mock()
    mock_context.get_state = Mock()
    mock_context.set_state = Mock()
    return mock_context


@pytest.fixture
def mock_middleware_context():
    """Create a mock MiddlewareContext for testing."""
    from fastmcp.server.middleware import MiddlewareContext

    mock_context = Mock(spec=MiddlewareContext)
    return mock_context
