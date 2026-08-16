"""Resolve package and documentation metadata for a release."""

from __future__ import annotations

import argparse
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


class ReleaseMetadataError(ValueError):
    """Raised when repository release metadata is incomplete or invalid."""


@dataclass(frozen=True)
class ReleaseMetadata:
    """Values shared by package and documentation release jobs."""

    version: str
    tag: str
    docs_version: str
    docs_config: str
    docs_directory: str


def load_release_metadata(root: Path = ROOT) -> ReleaseMetadata:
    """Read and validate release metadata from a repository checkout."""
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        raise ReleaseMetadataError(f"Project metadata does not exist: {pyproject}")

    with pyproject.open("rb") as project_file:
        document = tomllib.load(project_file)

    project = document.get("project")
    if not isinstance(project, dict):
        raise ReleaseMetadataError("pyproject.toml does not contain a [project] table")

    version = project.get("version")
    if not isinstance(version, str) or not SEMANTIC_VERSION.fullmatch(version):
        raise ReleaseMetadataError(
            "[project].version must be a stable semantic version such as 2.0.0"
        )

    major = version.split(".", maxsplit=1)[0]
    docs_version = f"v{major}"
    docs_config = f"mkdocs.{docs_version}.yml"
    docs_directory = f"docs/{docs_version}"

    if not (root / docs_config).is_file():
        raise ReleaseMetadataError(
            f"Documentation configuration does not exist: {docs_config}"
        )
    if not (root / docs_directory).is_dir():
        raise ReleaseMetadataError(
            f"Documentation source directory does not exist: {docs_directory}"
        )

    return ReleaseMetadata(
        version=version,
        tag=f"v{version}",
        docs_version=docs_version,
        docs_config=docs_config,
        docs_directory=docs_directory,
    )


def write_github_output(path: Path, metadata: ReleaseMetadata) -> None:
    """Append release metadata to a GitHub Actions output file."""
    values = {
        "version": metadata.version,
        "tag": metadata.tag,
        "docs_version": metadata.docs_version,
        "docs_config": metadata.docs_config,
        "docs_directory": metadata.docs_directory,
    }
    with path.open("a", encoding="utf-8") as output:
        for name, value in values.items():
            output.write(f"{name}={value}\n")


def command_line() -> argparse.Namespace:
    """Parse optional GitHub Actions output handling."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--github-output",
        type=Path,
        help="append name=value pairs to this GitHub Actions output file",
    )
    return parser.parse_args()


def main() -> int:
    """Validate and print the release metadata for this checkout."""
    arguments = command_line()
    metadata = load_release_metadata()

    if arguments.github_output is not None:
        write_github_output(arguments.github_output, metadata)

    print(f"Package version: {metadata.version}")
    print(f"Git tag: {metadata.tag}")
    print(f"Documentation version: {metadata.docs_version}")
    print(f"Documentation config: {metadata.docs_config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
