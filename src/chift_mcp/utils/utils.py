from typing import Any

from chift.openapi.models import (
    Connection,
    Consumer,
)
from mcp.server import FastMCP


def register_mcp_tools(mcp: FastMCP, tools: list[dict], consumer: Consumer) -> None:
    for tool_info in tools:
        tool_name = tool_info["name"]
        params = tool_info["params"]
        description = tool_info["description"]

        # Create parameter list and annotations
        param_list = []
        param_annotations = {}

        for param in params:
            # Parse parameter information
            if ":" in param:
                param_parts = param.split(":", 1)
                param_name = param_parts[0]
                param_type = param_parts[1]
            else:
                param_name = param
                param_type = "Any"

            # Handle default values
            if "=" in param_name:
                param_name, default_val = param_name.split("=", 1)
                param_list.append(f"{param_name}={default_val}")
            else:
                param_list.append(param_name)

            # Set type annotation
            if "=" in param_type:
                param_type = param_type.split("=")[0]

            if param_type == "str":
                param_annotations[param_name] = str
            elif param_type == "int":
                param_annotations[param_name] = int
            elif param_type == "float":
                param_annotations[param_name] = float
            elif param_type == "bool":
                param_annotations[param_name] = bool
            elif param_type == "dict":
                param_annotations[param_name] = dict
            elif "list" in param_type.lower():
                param_annotations[param_name] = list[Any]
            elif "chift.openapi.models" in param_type:
                # For model types we use Any for now
                param_annotations[param_name] = Any
            else:
                param_annotations[param_name] = Any

        # Function creation
        exec_globals = {"consumer": consumer, "List": list, "Any": Any}

        fn_def = f"""
def {tool_name}({", ".join(param_list)}):
    \"\"\"
    {description}
    \"\"\"
    return {tool_info["func"]}
"""

        exec(fn_def, exec_globals)

        # Get function and add annotations
        tool_fn = exec_globals[tool_name]
        tool_fn.__annotations__ = param_annotations

        # Set return type
        response_type = tool_info["response_type"]
        if response_type == "bool":
            tool_fn.__annotations__["return"] = bool
        elif response_type == "dict":
            tool_fn.__annotations__["return"] = dict
        elif response_type.startswith("list") or response_type.startswith("List"):
            tool_fn.__annotations__["return"] = list[Any]
        else:
            tool_fn.__annotations__["return"] = Any

        # Register with MCP
        mcp.tool()(tool_fn)


def map_connections_to_modules(connections: list[Connection]) -> set[str]:
    modules = []
    for connection in connections:
        if connection.api not in modules:
            modules.append(f"chift.models.consumers.{connection.api.lower()}")
    return set(modules)
