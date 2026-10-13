"""Smoke tests: verify the hft_jev package is importable and has a version."""

import pytest


@pytest.mark.unit
def test_package_is_importable() -> None:
    """The hft_jev package must be importable."""
    import hft_jev  # noqa: F401  — side-effect import is intentional


@pytest.mark.unit
def test_version_is_defined() -> None:
    """hft_jev.__version__ must be a non-empty string following PEP 440."""
    from hft_jev import __version__

    assert isinstance(__version__, str)
    assert len(__version__) > 0
    assert "." in __version__, f"Expected PEP 440 version, got {__version__!r}"
