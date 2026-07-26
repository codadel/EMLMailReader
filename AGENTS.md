# Agent instructions

This file applies to the entire repository. Keep it concise because it is
included in every agent interaction. Read the linked guidance only when it is
relevant to the current task.

## Always follow

- Inspect `git status` before editing and preserve unrelated user changes.
- Support Python 3.12 or newer and keep runtime code dependency-free unless the
  user explicitly approves a new dependency.
- Preserve the single canonical major-version API. Do not reintroduce legacy
  projections, compatibility modes, duplicate attachment/address classes, or
  multiple serialization schemas.
- Keep unit tests filesystem-free. Real EML files and all filesystem behavior
  belong in functional tests.
- Update package exports, tests, and public documentation together when public
  behavior changes.
- Maintain more than 95% branch coverage for every library module and for the
  package overall.
- Do not intentionally edit generated artifacts such as `.venv/`,
  `.pytest_cache/`, `htmlcov/`, `*.egg-info/`, `.coverage`, `.graphify*`, or
  `graphify-out/`.
- Do not commit, push, tag, publish, or otherwise modify external state unless
  the user explicitly requests it.

## Read before changing

- [Local workspace setup](ai-docs/SETUP.md): mise installation, workspace
  bootstrap, validation, and common development commands.
- [Library implementation](ai-docs/LIBRARY_IMPLEMENTATION.md): architecture,
  standards behavior, canonical data model, parsing contracts, diagnostics,
  MIME handling, and resource limits.
- [Test instructions](ai-docs/TEST_INSTRUCTIONS.md): unit/functional
  boundaries, pytest commands, mise tasks, and coverage workflow.
- [Code quality](ai-docs/QUALITY.md): Ruff, MyPy, pre-commit, manual fixes,
  check-only automation, and CI enforcement.
- [Release process](ai-docs/RELEASE.md): release authorization, versioning,
  branch, tagging, build, and PyPI publishing rules.
- [Public documentation](docs/index.md): current user-facing API reference.
- [README](README.md): installation and primary public usage.

## Required validation

Run the smallest relevant tests while developing. Before handoff, run:

```bash
mise run quality
mise run pre-commit
git diff --check
```

If mise is unavailable after the environment has been installed, use the
equivalent pytest commands documented in
[Test instructions](ai-docs/TEST_INSTRUCTIONS.md).
