import os

import pytest

from src.chift_mcp.utils.importer import (
    import_toolkit_functions,
    validate_config,
)


def test_validate_config_type_error():
    with pytest.raises(ValueError):
        validate_config(None)


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
