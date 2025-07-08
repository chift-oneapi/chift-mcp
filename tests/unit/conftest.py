import pytest


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
