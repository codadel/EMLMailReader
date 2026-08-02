"""Run version-aware MkDocs commands for repository documentation."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def documentation_version(value: str) -> str:
    """Normalize and validate a major documentation version."""
    version = value.lower()
    if not version.startswith("v"):
        version = f"v{version}"
    if not version[1:].isdigit():
        raise argparse.ArgumentTypeError("version must look like v1, v2, or 2")
    return version


def command_line() -> argparse.Namespace:
    """Parse the requested MkDocs action and major version."""
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("build", "serve"))
    parser.add_argument("version", nargs="?", default="v2", type=documentation_version)
    return parser.parse_args()


def validate_python_examples(docs_directory: Path) -> None:
    """Compile every Python example in a documentation source tree."""
    for page in sorted(docs_directory.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        for index, match in enumerate(PYTHON_BLOCK.finditer(text), start=1):
            source = textwrap.dedent(match.group(1))
            if len(source.splitlines()) < 2:
                continue
            stripped = source.lstrip()
            if "->" in source and not stripped.startswith(("def ", "async def ")):
                continue
            if re.match(r"[A-Za-z_]\w*\(\n", stripped) and re.search(
                r"(?m)^\s+\w+\s*:\s*", source
            ):
                continue
            try:
                compile(source, f"{page}#python-{index}", "exec")
            except SyntaxError as error:
                raise SystemExit(
                    f"Invalid Python example in {page} block {index}: {error}"
                ) from error


def main() -> int:
    """Validate the versioned source and execute MkDocs."""
    arguments = command_line()
    docs_directory = ROOT / "docs" / arguments.version
    config = ROOT / f"mkdocs.{arguments.version}.yml"

    if not docs_directory.is_dir():
        raise SystemExit(f"Documentation directory does not exist: {docs_directory}")
    if not config.is_file():
        raise SystemExit(f"MkDocs configuration does not exist: {config}")

    if arguments.action == "build":
        validate_python_examples(docs_directory)

    command = [
        sys.executable,
        "-m",
        "mkdocs",
        arguments.action,
        "--config-file",
        str(config),
    ]
    if arguments.action == "build":
        command.append("--strict")

    try:
        return subprocess.run(command, cwd=ROOT, check=False).returncode
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
