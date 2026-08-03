"""Tests for TestPyPI release-candidate metadata preparation."""

import json
from email.message import Message
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from scripts.test_release_metadata import (
    TestReleaseMetadata as ReleaseCandidateMetadata,
)
from scripts.test_release_metadata import (
    TestReleaseMetadataError as ReleaseCandidateMetadataError,
)
from scripts.test_release_metadata import (
    fetch_testpypi_versions,
    next_release_candidate,
    resolve_test_release_metadata,
    write_candidate_version,
    write_github_output,
)


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


def test_next_release_candidate_starts_at_rc1() -> None:
    assert next_release_candidate("2.0.0", set()) == "2.0.0rc1"


def test_next_release_candidate_increments_highest_matching_rc() -> None:
    releases = {"1.0.0", "2.0.0rc1", "2.0.0rc3", "2.1.0rc9", "invalid"}

    assert next_release_candidate("2.0.0", releases) == "2.0.0rc4"


def test_next_release_candidate_rejects_existing_final_version() -> None:
    with pytest.raises(ReleaseCandidateMetadataError, match="already exists"):
        next_release_candidate("2.0.0", {"2.0.0", "2.0.0rc1"})


def test_fetch_testpypi_versions_reads_release_keys() -> None:
    response = BytesIO(json.dumps({"releases": {"2.0.0rc1": []}}).encode())

    with patch("scripts.test_release_metadata.urlopen", return_value=response):
        assert fetch_testpypi_versions("example project") == {"2.0.0rc1"}


def test_fetch_testpypi_versions_treats_missing_project_as_empty() -> None:
    error = HTTPError("url", 404, "Not Found", Message(), None)

    with patch("scripts.test_release_metadata.urlopen", side_effect=error):
        assert fetch_testpypi_versions("new-project") == set()


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (HTTPError("url", 503, "Unavailable", Message(), None), "HTTP 503"),
        (URLError("offline"), "Could not read release metadata"),
    ],
)
def test_fetch_testpypi_versions_rejects_index_failures(
    error: HTTPError | URLError, message: str
) -> None:
    with (
        patch("scripts.test_release_metadata.urlopen", side_effect=error),
        pytest.raises(ReleaseCandidateMetadataError, match=message),
    ):
        fetch_testpypi_versions("example-project")


@pytest.mark.parametrize("payload", [[], {}, {"releases": []}])
def test_fetch_testpypi_versions_rejects_invalid_responses(payload: object) -> None:
    response = BytesIO(json.dumps(payload).encode())

    with (
        patch("scripts.test_release_metadata.urlopen", return_value=response),
        pytest.raises(ReleaseCandidateMetadataError, match=r"invalid|releases table"),
    ):
        fetch_testpypi_versions("example-project")


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
