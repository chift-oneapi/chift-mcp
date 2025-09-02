import chift

from chift_mcp.config import Chift
from chift_mcp.constants import CHIFT_DOMAINS, CHIFT_OPERATION_TYPES


def configure_chift(chift_config: Chift) -> None:
    """Configure global Chift client settings."""
    chift.client_secret = chift_config.client_secret.get_secret_value()
    chift.client_id = chift_config.client_id
    chift.account_id = chift_config.account_id
    chift.url_base = chift_config.url_base


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
