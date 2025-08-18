import importlib.util
import inspect
import os
import sys

from collections.abc import Callable
from functools import wraps

import chift

from loguru import logger
from mcp.server import FastMCP

from chift_mcp.constants import CHIFT_DOMAINS, CHIFT_OPERATION_TYPES
from chift_mcp.utils.utils import CONNECTION_TYPES


def get_connection_types(consumer_id: str | None = None) -> list[str]:
    """
    Get the connection types for a consumer.

    Args:
        consumer_id (str): The consumer ID

    Returns:
        list[str]: The connection types
    """
    if consumer_id is None:
        return list(CONNECTION_TYPES.values())

    consumer = chift.Consumer.get(chift_id=consumer_id)

    connections = consumer.Connection.all()

    return [CONNECTION_TYPES[connection.api] for connection in connections]


def validate_config(function_config: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Validates and deduplicates Chift domain operation configuration.

    Args:
        function_config (dict): Dictionary with configuration {domain: [operation_types]}

    Returns:
        dict: Validated and deduplicated configuration

    Raises:
        ValueError: If configuration is invalid

    Example:
        >>> config = {"accounting": ["get", "get", "update"], "commerce": ["update"]}
        >>> validate_config(config)
        {"accounting": ["get", "update"], "commerce": ["update"]}

        >>> invalid_config = {"accounting": ["invalid_operation"]}
        >>> validate_config(invalid_config)
        ValueError: Invalid configuration. Check domains and operation types.
    """

    # Check if config is a dictionary
    if not isinstance(function_config, dict):
        raise ValueError("Configuration must be a dictionary")

    result_config = {}

    # Check each key and value
    for domain, operations in function_config.items():
        # Check if domain is supported
        if domain not in CHIFT_DOMAINS:
            raise ValueError(f"Invalid domain: {domain}")

        # Check if operations is a list
        if not isinstance(operations, list):
            raise ValueError(f"Operations for domain {domain} must be a list")

        # Deduplicate operations
        unique_operations = []
        for operation in operations:
            # Check if operation is supported
            if operation not in CHIFT_OPERATION_TYPES:
                raise ValueError(f"Invalid operation type: {operation}")

            # Add only unique operations
            if operation not in unique_operations:
                unique_operations.append(operation)

        result_config[domain] = unique_operations

    return result_config


def create_wrapper_without_consumer_id(func: Callable, consumer_id: str) -> Callable:
    """
    Creates a wrapper function that removes consumer_id parameter and injects it automatically.

    Args:
        func: The original function that has consumer_id as first parameter
        consumer_id: The consumer_id value to inject

    Returns:
        Wrapped function without consumer_id parameter
    """
    # Get the original function signature
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    # Check if consumer_id is the first parameter
    if not params or params[0].name != "consumer_id":
        return func  # Return original if consumer_id is not the first parameter

    # Create new parameters list without consumer_id
    new_params = params[1:]  # Skip the first parameter (consumer_id)
    new_sig = sig.replace(parameters=new_params)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Inject consumer_id as the first argument
        return func(consumer_id, *args, **kwargs)

    # Update the wrapper's signature
    setattr(wrapper, "__signature__", new_sig)  # noqa: B010

    # Update docstring to reflect the parameter change
    if func.__doc__:
        lines = func.__doc__.split("\n")
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            # Skip the consumer_id parameter documentation
            if "consumer_id (str): The consumer ID" in line:
                # Skip this line and continue until we find the next parameter or section
                i += 1
                continue
            else:
                new_lines.append(line)
            i += 1

        wrapper.__doc__ = "\n".join(new_lines)

    return wrapper


def import_toolkit_functions(config: dict, mcp: FastMCP, consumer_id: str | None = None) -> None:
    # Validate configuration
    config = validate_config(config)

    # Find project root (directory containing chift_mcp)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    while (
        os.path.basename(project_root) != "chift_mcp"
        and os.path.dirname(project_root) != project_root
    ):
        project_root = os.path.dirname(project_root)

    # If we are in chift_mcp directory, go one level up
    if os.path.basename(project_root) == "chift_mcp":
        project_root = os.path.dirname(project_root)

    # Path to toolkit.py from project root
    file_path = os.path.join(project_root, "chift_mcp", "tools", "toolkit.py")

    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Load module
    spec = importlib.util.spec_from_file_location("chift_mcp.tools.toolkit", file_path)
    if not spec:
        raise ImportError(f"Failed to load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    if not module:
        raise ImportError(f"Failed to load module from {file_path}")

    sys.modules["chift_mcp.tools.toolkit"] = module
    if not spec.loader:
        raise ImportError(f"Failed to load module from {file_path}")
    spec.loader.exec_module(module)

    connection_types = get_connection_types(consumer_id)

    # Get all functions from module that match configuration
    matching_functions = {}
    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and not name.startswith("__"):
            # Split name by underscore and check if domain+operation match config
            parts = name.split("_", 2)  # Split into max 3 parts
            if len(parts) >= 2:  # Need at least domain and operation
                domain, operation = parts[0], parts[1]

                if (
                    domain not in connection_types
                ):  # Check if domain is supported for the consumer, never skips if consumer_id is None  # noqa: E501
                    continue

                # Check if domain and operation are in config
                if domain in config and operation in config[domain]:
                    # Apply wrapper if consumer_id is provided and function has consumer_id param
                    tool_func = obj
                    if consumer_id:
                        sig = inspect.signature(obj)
                        params = list(sig.parameters.values())
                        if params and params[0].name == "consumer_id":
                            tool_func = create_wrapper_without_consumer_id(obj, consumer_id)

                    matching_functions[name] = tool_func

                    # Get function docstring as description
                    description = tool_func.__doc__.strip() if tool_func.__doc__ else None

                    # Register as tool
                    try:
                        mcp.add_tool(tool_func, name=name, description=description)
                    except Exception as e:
                        logger.error(f"Error registering tool {name}: {e}")

    logger.info(
        f"Imported {len(matching_functions)} functions from toolkit.py based on configuration:"
    )
    for name in matching_functions:
        logger.info(f"- {name}")
