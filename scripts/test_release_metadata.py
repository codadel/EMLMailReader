"""Resolve and prepare an unused TestPyPI release-candidate version."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

from scripts.release_metadata import SEMANTIC_VERSION

ROOT = Path(__file__).resolve().parents[1]
TESTPYPI_PROJECT_URL = "https://test.pypi.org/pypi/{project}/json"
PROJECT_HEADER = re.compile(r"^\[project\]\s*$")
TABLE_HEADER = re.compile(r"^\[")
VERSION_ASSIGNMENT = re.compile(r"^(?P<indent>\s*)version\s*=")


class TestReleaseMetadataError(ValueError):
    """Raised when a safe TestPyPI candidate cannot be prepared."""


@dataclass(frozen=True)
class TestReleaseMetadata:
    """Package values for one TestPyPI publication."""

    project_name: str
    base_version: str
    version: str


def load_project_metadata(root: Path = ROOT) -> tuple[str, str]:
    """Read and validate the project name and stable base version."""
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        raise TestReleaseMetadataError(f"Project metadata does not exist: {pyproject}")

    with pyproject.open("rb") as project_file:
        document = tomllib.load(project_file)

    project = document.get("project")
    if not isinstance(project, dict):
        raise TestReleaseMetadataError(
            "pyproject.toml does not contain a [project] table"
        )

    project_name = project.get("name")
    if not isinstance(project_name, str) or not project_name.strip():
        raise TestReleaseMetadataError("[project].name must be a non-empty string")

    base_version = project.get("version")
    if not isinstance(base_version, str) or not SEMANTIC_VERSION.fullmatch(
        base_version
    ):
        raise TestReleaseMetadataError(
            "[project].version must be a stable semantic version such as 2.0.0"
        )
    return project_name, base_version


def fetch_testpypi_versions(project_name: str) -> set[str]:
    """Return every version currently registered for a TestPyPI project."""
    project_url = TESTPYPI_PROJECT_URL.format(project=quote(project_name, safe=""))
    try:
        with urlopen(project_url, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return set()
        raise TestReleaseMetadataError(
            f"TestPyPI returned HTTP {error.code} for {project_name}"
        ) from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise TestReleaseMetadataError(
            f"Could not read release metadata for {project_name} from TestPyPI"
        ) from error

    if not isinstance(payload, dict):
        raise TestReleaseMetadataError("TestPyPI returned an invalid project response")
    releases = payload.get("releases")
    if not isinstance(releases, dict) or not all(
        isinstance(version, str) for version in releases
    ):
        raise TestReleaseMetadataError(
            "TestPyPI project response does not contain a valid releases table"
        )
    return set(releases)


def next_release_candidate(base_version: str, releases: set[str]) -> str:
    """Select the next unused ``base_version`` release candidate."""
    if base_version in releases:
        raise TestReleaseMetadataError(
            f"Final version {base_version} already exists on TestPyPI; "
            "increase [project].version before publishing another candidate"
        )

    candidate_pattern = re.compile(rf"{re.escape(base_version)}rc([1-9]\d*)")
    release_candidates = [
        int(match.group(1))
        for version in releases
        if (match := candidate_pattern.fullmatch(version)) is not None
    ]
    next_number = max(release_candidates, default=0) + 1
    candidate = f"{base_version}rc{next_number}"
    if candidate in releases:
        raise TestReleaseMetadataError(
            f"Could not select an unused TestPyPI version for {base_version}"
        )
    return candidate


def resolve_test_release_metadata(root: Path = ROOT) -> TestReleaseMetadata:
    """Validate the base version and resolve its next TestPyPI candidate."""
    project_name, base_version = load_project_metadata(root)
    versions = fetch_testpypi_versions(project_name)
    candidate = next_release_candidate(base_version, versions)
    return TestReleaseMetadata(
        project_name=project_name,
        base_version=base_version,
        version=candidate,
    )


def write_candidate_version(metadata: TestReleaseMetadata, root: Path = ROOT) -> None:
    """Replace the project version in the current checkout with the candidate."""
    pyproject = root / "pyproject.toml"
    lines = pyproject.read_text(encoding="utf-8").splitlines(keepends=True)
    in_project_table = False
    replacements = 0

    for index, line in enumerate(lines):
        stripped = line.strip()
        if PROJECT_HEADER.fullmatch(stripped):
            in_project_table = True
            continue
        if in_project_table and TABLE_HEADER.match(stripped):
            in_project_table = False
        if not in_project_table:
            continue

        assignment = VERSION_ASSIGNMENT.match(line)
        if assignment is None:
            continue
        newline = "\n" if line.endswith("\n") else ""
        lines[index] = (
            f'{assignment.group("indent")}version = "{metadata.version}"{newline}'
        )
        replacements += 1

    if replacements != 1:
        raise TestReleaseMetadataError(
            "Expected exactly one version assignment in the [project] table"
        )
    pyproject.write_text("".join(lines), encoding="utf-8")


def write_github_output(path: Path, metadata: TestReleaseMetadata) -> None:
    """Append TestPyPI metadata to a GitHub Actions output file."""
    values = {
        "project_name": metadata.project_name,
        "base_version": metadata.base_version,
        "version": metadata.version,
    }
    with path.open("a", encoding="utf-8") as output:
        for name, value in values.items():
            output.write(f"{name}={value}\n")


def command_line() -> argparse.Namespace:
    """Parse candidate preparation and GitHub Actions output options."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-version",
        action="store_true",
        help="replace [project].version in this checkout with the candidate",
    )
    parser.add_argument(
        "--github-output",
        type=Path,
        help="append name=value pairs to this GitHub Actions output file",
    )
    return parser.parse_args()


def main() -> int:
    """Validate, display, and optionally apply TestPyPI candidate metadata."""
    arguments = command_line()
    try:
        metadata = resolve_test_release_metadata()
    except TestReleaseMetadataError as error:
        print(f"TestPyPI metadata validation failed: {error}", file=sys.stderr)
        return 1

    if arguments.write_version:
        write_candidate_version(metadata)
    if arguments.github_output is not None:
        write_github_output(arguments.github_output, metadata)

    print(f"Project: {metadata.project_name}")
    print(f"Base version: {metadata.base_version}")
    print(f"TestPyPI version: {metadata.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
