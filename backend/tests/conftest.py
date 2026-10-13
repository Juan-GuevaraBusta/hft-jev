"""Pytest configuration for hft_jev tests."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers declared in pyproject.toml."""
    config.addinivalue_line("markers", "unit: unit tests (fast, no external dependencies)")
    config.addinivalue_line("markers", "integration: integration tests (require Floci/PostgreSQL)")
