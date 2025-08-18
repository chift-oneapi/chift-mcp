import inspect
import os

import pytest

from src.chift_mcp.utils.importer import (
    create_wrapper_without_consumer_id,
    import_toolkit_functions,
    validate_config,
)


@pytest.mark.parametrize(
    "cfg, expected",
    [
        ({"accounting": ["get", "get", "update"]}, {"accounting": ["get", "update"]}),
        ({"commerce": []}, {"commerce": []}),
        ({}, {}),
    ],
)
def test_validate_config_success(cfg, expected):
    assert validate_config(cfg) == expected


@pytest.mark.parametrize(
    "cfg",
    [
        {"invalid_domain": ["get"]},
        {"accounting": "not a list"},
        {"accounting": ["invalid_operation"]},
    ],
)
def test_validate_config_failure(cfg):
    with pytest.raises(ValueError):
        validate_config(cfg)


def test_import_toolkit_functions_file_not_found(monkeypatch, dummy_mcp):
    monkeypatch.setattr(os.path, "exists", lambda _: False)
    with pytest.raises(FileNotFoundError):
        import_toolkit_functions({}, dummy_mcp)


# Test functions for consumer_id wrapper functionality
def sample_function_with_consumer_id(
    consumer_id: str, limit: int = 50, search: str | None = None
) -> list:
    """Sample function that takes consumer_id as first parameter.

    Args:
        consumer_id (str): The consumer ID
        limit (int): Maximum number of items to return
        search (str): Search term

    Returns:
        list: Sample return value
    """
    return [f"consumer: {consumer_id}, limit: {limit}, search: {search}"]


def sample_function_without_consumer_id(limit: int = 50, search: str | None = None) -> list:
    """Sample function that doesn't take consumer_id as first parameter.

    Args:
        limit (int): Maximum number of items to return
        search (str): Search term

    Returns:
        list: Sample return value
    """
    return [f"limit: {limit}, search: {search}"]


def sample_function_consumer_id_not_first(data: dict, consumer_id: str) -> dict:
    """Sample function where consumer_id is not the first parameter.

    Args:
        data (dict): Some data
        consumer_id (str): The consumer ID

    Returns:
        dict: Sample return value
    """
    return {"data": data, "consumer_id": consumer_id}


def sample_function_with_typehints(
    consumer_id: str, limit: int = 50, search: str | None = None, tags: list[str] | None = None
) -> list[dict]:
    """Sample function with comprehensive type hints.

    Args:
        consumer_id (str): The consumer ID
        limit (int): Maximum number of items to return
        search (str | None): Search term
        tags (list[str] | None): List of tags to filter by

    Returns:
        list[dict]: Sample return value
    """
    return [{"consumer_id": consumer_id, "limit": limit, "search": search, "tags": tags}]


class TestCreateWrapperWithoutConsumerId:
    """Test cases for create_wrapper_without_consumer_id function."""

    def test_wrapper_removes_consumer_id_parameter(self):
        """Test that wrapper removes consumer_id parameter from function signature."""
        original_func = sample_function_with_consumer_id
        wrapped_func = create_wrapper_without_consumer_id(original_func, "test_consumer_123")

        original_sig = inspect.signature(original_func)
        wrapped_sig = inspect.signature(wrapped_func)

        # Check that consumer_id parameter is removed
        assert "consumer_id" in original_sig.parameters
        assert "consumer_id" not in wrapped_sig.parameters

        # Check that other parameters remain
        assert "limit" in wrapped_sig.parameters
        assert "search" in wrapped_sig.parameters

        # Check parameter order and defaults are preserved
        wrapped_params = list(wrapped_sig.parameters.values())
        assert wrapped_params[0].name == "limit"
        assert wrapped_params[0].default == 50
        assert wrapped_params[1].name == "search"
        assert wrapped_params[1].default is None

    def test_wrapper_injects_consumer_id(self):
        """Test that wrapper correctly injects consumer_id when calling the original function."""
        original_func = sample_function_with_consumer_id
        test_consumer_id = "test_consumer_456"
        wrapped_func = create_wrapper_without_consumer_id(original_func, test_consumer_id)

        # Call wrapped function without consumer_id
        result = wrapped_func(limit=25, search="test_search")

        # Check that consumer_id was injected
        assert len(result) == 1
        assert test_consumer_id in result[0]
        assert "limit: 25" in result[0]
        assert "search: test_search" in result[0]

    def test_wrapper_with_positional_args(self):
        """Test that wrapper works correctly with positional arguments."""
        original_func = sample_function_with_consumer_id
        test_consumer_id = "test_consumer_789"
        wrapped_func = create_wrapper_without_consumer_id(original_func, test_consumer_id)

        # Call with positional arguments
        result = wrapped_func(100, "positional_search")

        assert test_consumer_id in result[0]
        assert "limit: 100" in result[0]
        assert "search: positional_search" in result[0]

    def test_wrapper_with_mixed_args(self):
        """Test that wrapper works correctly with mixed positional and keyword arguments."""
        original_func = sample_function_with_consumer_id
        test_consumer_id = "test_consumer_mixed"
        wrapped_func = create_wrapper_without_consumer_id(original_func, test_consumer_id)

        # Call with mixed arguments
        result = wrapped_func(75, search="mixed_search")

        assert test_consumer_id in result[0]
        assert "limit: 75" in result[0]
        assert "search: mixed_search" in result[0]

    def test_wrapper_returns_original_if_no_consumer_id_param(self):
        """Test that wrapper returns original function if consumer_id is not the first parameter."""
        original_func = sample_function_without_consumer_id
        wrapped_func = create_wrapper_without_consumer_id(original_func, "test_consumer")

        # Should return the exact same function object
        assert wrapped_func is original_func

    def test_wrapper_returns_original_if_consumer_id_not_first(self):
        """Test that wrapper returns original function if consumer_id exists but is not first parameter."""
        original_func = sample_function_consumer_id_not_first
        wrapped_func = create_wrapper_without_consumer_id(original_func, "test_consumer")

        # Should return the exact same function object
        assert wrapped_func is original_func

    def test_wrapper_modifies_docstring(self):
        """Test that wrapper removes consumer_id parameter from docstring."""
        original_func = sample_function_with_consumer_id
        wrapped_func = create_wrapper_without_consumer_id(original_func, "test_consumer")

        original_doc = original_func.__doc__
        wrapped_doc = wrapped_func.__doc__

        # Original should contain consumer_id documentation
        assert original_doc is not None and "consumer_id (str): The consumer ID" in original_doc

        # Wrapped should not contain consumer_id documentation
        assert wrapped_doc is not None and "consumer_id (str): The consumer ID" not in wrapped_doc

        # Other parts of docstring should remain
        assert "limit (int): Maximum number of items to return" in wrapped_doc
        assert "search (str): Search term" in wrapped_doc
        assert "Returns:" in wrapped_doc

    def test_wrapper_preserves_function_name(self):
        """Test that wrapper preserves the original function name."""
        original_func = sample_function_with_consumer_id
        wrapped_func = create_wrapper_without_consumer_id(original_func, "test_consumer")

        assert wrapped_func.__name__ == original_func.__name__

    def test_wrapper_handles_function_without_docstring(self):
        """Test that wrapper handles functions without docstrings gracefully."""

        def func_without_doc(consumer_id: str, value: int) -> int:
            return value * 2

        wrapped_func = create_wrapper_without_consumer_id(func_without_doc, "test_consumer")

        # Should not raise an error
        result = wrapped_func(5)
        assert result == 10

        # Signature should be updated
        sig = inspect.signature(wrapped_func)
        assert "consumer_id" not in sig.parameters
        assert "value" in sig.parameters

    def test_wrapper_handles_empty_function(self):
        """Test that wrapper handles functions with no parameters."""

        def empty_func() -> str:
            return "empty"

        wrapped_func = create_wrapper_without_consumer_id(empty_func, "test_consumer")

        # Should return the original function since no consumer_id parameter
        assert wrapped_func is empty_func

    def test_wrapper_preserves_type_hints(self):
        """Test that wrapper preserves type hints for all parameters and return type."""
        original_func = sample_function_with_typehints
        wrapped_func = create_wrapper_without_consumer_id(original_func, "test_consumer")

        original_sig = inspect.signature(original_func)
        wrapped_sig = inspect.signature(wrapped_func)

        # Check that consumer_id parameter is removed
        assert "consumer_id" in original_sig.parameters
        assert "consumer_id" not in wrapped_sig.parameters

        # Get parameter dictionaries for easier access
        wrapped_params = {p.name: p for p in wrapped_sig.parameters.values()}

        # Verify type hints are preserved for remaining parameters
        assert wrapped_params["limit"].annotation is int
        assert wrapped_params["search"].annotation == str | None
        assert wrapped_params["tags"].annotation == list[str] | None

        # Verify defaults are preserved
        assert wrapped_params["limit"].default == 50
        assert wrapped_params["search"].default is None
        assert wrapped_params["tags"].default is None

        # Verify return type annotation is preserved
        assert wrapped_sig.return_annotation == list[dict]
        assert wrapped_sig.return_annotation == original_sig.return_annotation

    def test_wrapper_preserves_parameter_kinds(self):
        """Test that wrapper preserves parameter kinds (positional, keyword, etc.)."""

        def func_with_various_params(
            consumer_id: str, pos_only: int, /, normal: str, *args, kw_only: bool = True, **kwargs
        ) -> dict:
            return {}

        wrapped_func = create_wrapper_without_consumer_id(func_with_various_params, "test")
        wrapped_sig = inspect.signature(wrapped_func)
        wrapped_params = list(wrapped_sig.parameters.values())

        # Check parameter kinds are preserved
        assert wrapped_params[0].name == "pos_only"
        assert wrapped_params[0].kind == inspect.Parameter.POSITIONAL_ONLY

        assert wrapped_params[1].name == "normal"
        assert wrapped_params[1].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD

        assert wrapped_params[2].name == "args"
        assert wrapped_params[2].kind == inspect.Parameter.VAR_POSITIONAL

        assert wrapped_params[3].name == "kw_only"
        assert wrapped_params[3].kind == inspect.Parameter.KEYWORD_ONLY
        assert wrapped_params[3].default is True

        assert wrapped_params[4].name == "kwargs"
        assert wrapped_params[4].kind == inspect.Parameter.VAR_KEYWORD

    def test_wrapper_function_execution_with_typehints(self):
        """Test that wrapped function with type hints executes correctly."""
        original_func = sample_function_with_typehints
        test_consumer_id = "test_consumer_typehints"
        wrapped_func = create_wrapper_without_consumer_id(original_func, test_consumer_id)

        # Call wrapped function
        result = wrapped_func(limit=25, search="test_search", tags=["tag1", "tag2"])

        # Verify result structure and content
        assert len(result) == 1
        assert isinstance(result, list)
        assert isinstance(result[0], dict)

        result_data = result[0]
        assert result_data["consumer_id"] == test_consumer_id
        assert result_data["limit"] == 25
        assert result_data["search"] == "test_search"
        assert result_data["tags"] == ["tag1", "tag2"]
