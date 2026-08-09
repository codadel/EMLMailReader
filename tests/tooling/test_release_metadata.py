"""Tooling tests for the filesystem-backed release metadata resolver."""

from pathlib import Path

import pytest

from scripts.release_metadata import (
    ReleaseMetadataError,
    load_release_metadata,
    write_github_output,
)

pytestmark = pytest.mark.tooling


def create_release_project(root: Path, version: str = "2.3.4") -> None:
    """Create the minimal repository structure needed for release metadata."""
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "example"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (root / "docs" / "v2").mkdir(parents=True)
    (root / "mkdocs.v2.yml").write_text("INHERIT: mkdocs.yml\n", encoding="utf-8")


def test_load_release_metadata_selects_matching_major_docs(tmp_path: Path) -> None:
    create_release_project(tmp_path)

    metadata = load_release_metadata(tmp_path)

    assert metadata.version == "2.3.4"
    assert metadata.tag == "v2.3.4"
    assert metadata.docs_version == "v2"
    assert metadata.docs_config == "mkdocs.v2.yml"
    assert metadata.docs_directory == "docs/v2"


@pytest.mark.parametrize("version", ["2", "2.0", "2.0.0rc1", "02.0.0"])
def test_load_release_metadata_rejects_non_stable_versions(
    tmp_path: Path, version: str
) -> None:
    create_release_project(tmp_path, version)

    with pytest.raises(ReleaseMetadataError, match="stable semantic version"):
        load_release_metadata(tmp_path)


def test_load_release_metadata_requires_matching_docs_config(tmp_path: Path) -> None:
    create_release_project(tmp_path)
    (tmp_path / "mkdocs.v2.yml").unlink()

    with pytest.raises(ReleaseMetadataError, match="configuration does not exist"):
        load_release_metadata(tmp_path)


def test_load_release_metadata_requires_matching_docs_directory(
    tmp_path: Path,
) -> None:
    create_release_project(tmp_path)
    (tmp_path / "docs" / "v2").rmdir()

    with pytest.raises(ReleaseMetadataError, match="source directory does not exist"):
        load_release_metadata(tmp_path)


def test_write_github_output_exports_every_value(tmp_path: Path) -> None:
    create_release_project(tmp_path)
    metadata = load_release_metadata(tmp_path)
    output = tmp_path / "github-output.txt"

    write_github_output(output, metadata)

    assert output.read_text(encoding="utf-8").splitlines() == [
        "version=2.3.4",
        "tag=v2.3.4",
        "docs_version=v2",
        "docs_config=mkdocs.v2.yml",
        "docs_directory=docs/v2",
    ]
