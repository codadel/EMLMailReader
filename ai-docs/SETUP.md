# Local workspace setup

Use these instructions to prepare a development workspace after cloning the
repository.

## Prerequisite

Install [mise](https://mise.jdx.dev/) and open a terminal in the repository
root:

```bash
cd /path/to/EMLMailReader
```

If mise asks whether the repository configuration is trusted, approve it with:

```bash
mise trust
```

## Install the workspace

Install the configured Python version, then set up the project:

```bash
mise install
mise run setup
```

The setup task:

- creates or reuses the project `.venv`;
- installs EMLMailReader in editable mode;
- installs the pinned development dependencies from `requirements.txt`; and
- installs the repository's check-only pre-commit hooks.

## Verify the workspace

Run the complete local validation:

```bash
mise run quality
mise run pre-commit
```

Both tasks are check-only and stop on the first failed check. A successful
workspace passes Ruff formatting and linting, strict MyPy analysis, all unit
and functional tests, branch coverage, and every pre-commit hook.

## Common development commands

```bash
mise run test
mise run lint
mise run typecheck
mise run format-check
```

Use the more focused or verbose test tasks when needed:

```bash
mise run unit
mise run functional
mise run tooling
mise run test-verbose
mise run coverage
mise run coverage-html
```

## Commands that modify files

Formatting and lint fixes are never applied by CI, the release workflow, or
pre-commit. Invoke them deliberately:

```bash
mise run format
mise run lint-fix
```

Review the resulting changes, then rerun:

```bash
mise run quality
mise run pre-commit
```

For test boundaries and direct pytest alternatives, see
[Test instructions](TEST_INSTRUCTIONS.md). For the complete Ruff, MyPy,
pre-commit, and CI policy, see [Code quality](QUALITY.md).
