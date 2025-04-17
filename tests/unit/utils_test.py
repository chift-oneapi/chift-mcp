import pytest


class DummyConsumer:
    def test_action(self):
        return "ok"


def test_register_mcp_tools_registers_and_annotates(dummy_mcp):
    consumer = DummyConsumer()
    tools = [
        {
            "name": "do_thing",
            "params": ["x:int", "y:str='hi'", "z"],
            "description": "Does a thing",
            "func": "consumer.test_action()",
            "response_type": "bool",
        }
    ]

    register_mcp_tools(dummy_mcp, tools, consumer)

    assert len(dummy_mcp.tools) == 1
    fn = dummy_mcp.tools[0]
    assert fn.__name__ == "do_thing"
    assert fn.__doc__.strip() == "Does a thing"

    assert fn.__annotations__ == {
        "x": int,
        "y": str,
        "z": Any,
        "return": bool,
    }
    assert fn(1) == "ok"


@pytest.mark.parametrize(
    "apis, expected",
    [
        (["Test"], {"chift.models.consumers.test"}),
        (["A", "B", "A"], {"chift.models.consumers.a", "chift.models.consumers.b"}),
        ([], set()),
    ],
)
def test_map_connections_to_modules(apis, expected):
    class C:
        def __init__(self, api):
            self.api = api  # tests/test_tools_register.py


from typing import Any

import pytest

from src.chift_mcp.utils.utils import (
    map_connections_to_modules,
    register_mcp_tools,
)


class DummyConsumer:
    def test_action(self):
        return "ok"


def test_register_mcp_tools_registers_and_annotates(dummy_mcp):
    consumer = DummyConsumer()
    tools = [
        {
            "name": "do_thing",
            "params": ["x:int", "y:str='hi'", "z"],
            "description": "Does a thing",
            "func": "consumer.test_action()",
            "response_type": "bool",
        }
    ]

    register_mcp_tools(dummy_mcp, tools, consumer)

    assert len(dummy_mcp.tools) == 1
    fn = dummy_mcp.tools[0]

    assert fn.__name__ == "do_thing"
    assert fn.__doc__.strip() == "Does a thing"

    assert fn.__annotations__ == {
        "x": int,
        "y": str,
        "z": Any,
        "return": bool,
    }

    assert fn(1, z=None, y=None) == "ok"


@pytest.mark.parametrize(
    "apis, expected",
    [
        (["Test"], {"chift.models.consumers.test"}),
        (["A", "B", "A"], {"chift.models.consumers.a", "chift.models.consumers.b"}),
        ([], set()),
    ],
)
def test_map_connections_to_modules(apis, expected):
    class C:
        def __init__(self, api):
            self.api = api

    connections = [C(api) for api in apis]
    result = map_connections_to_modules(connections)
    assert result == expected

    connections = [C(api) for api in apis]
    result = map_connections_to_modules(connections)
    assert result == expected
