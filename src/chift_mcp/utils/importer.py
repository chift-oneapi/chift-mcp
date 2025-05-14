import importlib.util
import os
import sys

from loguru import logger
from mcp.server import FastMCP

from chift_mcp.constants import (
    CHIFT_DOMAINS,
    CHIFT_OPERATION_TYPES,
)


def validate_config(function_config: dict) -> dict:
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


def import_toolkit_functions(config: dict, mcp: FastMCP) -> None:
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
    module = importlib.util.module_from_spec(spec)
    sys.modules["chift_mcp.tools.toolkit"] = module
    spec.loader.exec_module(module)

    # Get all functions from module that match configuration
    matching_functions = {}
    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and not name.startswith("__"):
            # Split name by underscore and check if domain+operation match config
            parts = name.split("_", 2)  # Split into max 3 parts
            if len(parts) >= 2:  # Need at least domain and operation
                domain, operation = parts[0], parts[1]

                # Check if domain and operation are in config
                if domain in config and operation in config[domain]:
                    matching_functions[name] = obj

                    # Get function docstring as description
                    description = obj.__doc__.strip() if obj.__doc__ else None

                    # Register as tool
                    try:
                        mcp.add_tool(obj, name=name, description=description)
                    except Exception as e:
                        logger.error(f"Error registering tool {name}: {e}")

    logger.info(
        f"Imported {len(matching_functions)} functions from toolkit.py based on configuration:"
    )
    for name in matching_functions:
        logger.info(f"- {name}")
