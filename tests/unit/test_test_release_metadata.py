"""Filesystem-free unit tests for TestPyPI candidate selection and responses."""

import json
from email.message import Message
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from scripts.test_release_metadata import (
    TestReleaseMetadataError as ReleaseCandidateMetadataError,
)
from scripts.test_release_metadata import (
    fetch_testpypi_versions,
    next_release_candidate,
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
