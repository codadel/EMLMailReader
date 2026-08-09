"""Tooling checks for files shipped with the installed package."""

from importlib.resources import files

import pytest

pytestmark = pytest.mark.tooling


def test_installed_package_includes_pep561_marker() -> None:
    """Expose inline annotations to downstream static type checkers."""
    assert files("EMLMailReader").joinpath("py.typed").is_file()
