"""Filesystem-backed tooling tests for TestPyPI candidate preparation."""

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.test_release_metadata import (
    TestReleaseMetadata as ReleaseCandidateMetadata,
)
from scripts.test_release_metadata import (
    TestReleaseMetadataError as ReleaseCandidateMetadataError,
)
from scripts.test_release_metadata import (
    resolve_test_release_metadata,
    write_candidate_version,
    write_github_output,
)

pytestmark = pytest.mark.tooling


def create_test_release_project(root: Path, version: str = "2.0.0") -> None:
    """Create the minimal repository structure for TestPyPI metadata."""
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "example-project"\nversion = "{version}"\n',
        encoding="utf-8",
    )


def metadata(version: str = "2.0.0rc3") -> ReleaseCandidateMetadata:
    """Return representative resolved metadata."""
    return ReleaseCandidateMetadata(
        project_name="example-project",
        base_version="2.0.0",
        version=version,
    )


def test_resolve_test_release_metadata_uses_stable_version_without_docs(
    tmp_path: Path,
) -> None:
    create_test_release_project(tmp_path)

    with patch(
        "scripts.test_release_metadata.fetch_testpypi_versions",
        return_value={"2.0.0rc1"},
    ):
        resolved = resolve_test_release_metadata(tmp_path)

    assert resolved == metadata("2.0.0rc2")


def test_resolve_test_release_metadata_rejects_non_stable_base(
    tmp_path: Path,
) -> None:
    create_test_release_project(tmp_path, "2.0.0rc1")

    with pytest.raises(ReleaseCandidateMetadataError, match="stable semantic version"):
        resolve_test_release_metadata(tmp_path)


def test_write_candidate_version_changes_only_project_version(tmp_path: Path) -> None:
    create_test_release_project(tmp_path)
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[build-system]\nversion = "unchanged"\n\n'
        '[project]\nname = "example-project"\nversion = "2.0.0"\n',
        encoding="utf-8",
    )

    write_candidate_version(metadata(), tmp_path)

    assert pyproject.read_text(encoding="utf-8") == (
        '[build-system]\nversion = "unchanged"\n\n'
        '[project]\nname = "example-project"\nversion = "2.0.0rc3"\n'
    )


def test_write_candidate_version_requires_one_project_assignment(
    tmp_path: Path,
) -> None:
    create_test_release_project(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "example-project"\n', encoding="utf-8"
    )

    with pytest.raises(ReleaseCandidateMetadataError, match="exactly one"):
        write_candidate_version(metadata(), tmp_path)


def test_write_github_output_exports_candidate_values(tmp_path: Path) -> None:
    output = tmp_path / "github-output.txt"

    write_github_output(output, metadata())

    assert output.read_text(encoding="utf-8").splitlines() == [
        "project_name=example-project",
        "base_version=2.0.0",
        "version=2.0.0rc3",
    ]
