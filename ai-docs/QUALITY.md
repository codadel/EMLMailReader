# Code quality

The repository uses a Python-installed development toolchain:

- Ruff for formatting and linting
- MyPy for strict static type checking
- pre-commit for local commit-time enforcement
- pytest and Coverage.py for behavior and branch coverage

The package remains dependency-free at runtime. Exact development-tool
versions are pinned in `requirements.txt`, and their shared configuration is
stored in `pyproject.toml`.

## Setup

Follow [Local workspace setup](SETUP.md) for the initial mise, Python,
dependency, editable-package, and pre-commit installation. Reinstall the hook
separately when needed:

```bash
mise run hooks
```

## Check-only commands

These commands never change tracked files:

```bash
mise run format-check
mise run lint
mise run typecheck
mise run pre-commit
mise run quality
```

`mise run quality` checks Ruff formatting, Ruff lint rules, strict MyPy
analysis, tests, and branch coverage in sequence. It stops on the first failed
command.

The pre-commit hook checks the entire repository on every commit. It runs:

1. `ruff format --check`
2. `ruff check`
3. strict MyPy analysis for `EMLMailReader` and `tests`

The hook uses fail-fast behavior. It reports the first failed check, exits
non-zero, and leaves every file unchanged.

## Manual modification commands

Only invoke these commands when you deliberately want to change source files:

```bash
mise run format
mise run lint-fix
```

`format` applies Ruff formatting. `lint-fix` applies Ruff's safe automatic
lint fixes. Neither command is referenced by pre-commit, CI, the release
workflow, or `mise run quality`.

Review and stage any resulting changes manually before rerunning the check-only
commands.

## Continuous integration

The quality workflow runs on pull requests and pushes to `develop` or feature
branches. The release workflow runs the same checks before creating a tag,
building the package and matching documentation, or publishing either one.

Both workflows are read-only during quality validation and use normal
fail-fast GitHub Actions behavior. A failed formatting, lint, typing, test, or
coverage command terminates the job. No workflow formats code or applies lint
fixes.

## Required standard

- All library and test code must pass strict MyPy analysis.
- The installed package must include `EMLMailReader/py.typed`.
- Every library module and the package overall must retain more than 95%
  branch coverage.
- Suppressions must be narrow and justified. Do not add blanket MyPy ignores,
  broad Ruff exclusions, or unsafe automatic fixes.
