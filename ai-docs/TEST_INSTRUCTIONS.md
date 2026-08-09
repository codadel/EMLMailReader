# Test Instructions

This document provides instructions on how to run the test suite for the EMLMailReader library.

## Prerequisites

Prepare the Python environment, editable package, development dependencies,
and pre-commit hooks by following [Local workspace setup](SETUP.md).

The test toolchain uses:

- `pytest` as the test runner. It discovers the existing `unittest.TestCase`
  suite without requiring a rewrite.
- `pytest-cov` as the Coverage.py integration.
- `coverage` for persisted `.coverage` data and terminal or HTML reports.
- Ruff for non-mutating formatting and lint checks.
- MyPy for strict type checking of the library and tests.
- pre-commit for check-only, fail-fast commit validation.

See [Code quality](QUALITY.md) for manual formatting and lint-fix commands,
pre-commit behavior, and the complete quality workflow.

## Running All Tests

Run the concise test task:

```bash
mise run test
```

Pytest captures application logs from passing tests, which keeps expected
parser diagnostics out of the normal output. Captured output is included when
a test fails.

The suite has a strict boundary:

- `tests/unit/` contains tests that use only hard-coded, in-memory fixtures
  such as `bytes`, `str`, `BytesIO`, and `StringIO`. They do not read or write
  files.
- `tests/functional/` contains tests that parse committed `.eml` files from
  `tests/functional/assets/` and `tests/functional/fixtures/` through
  `MailReader.get_email`, and covers filesystem workflows such as attachment
  and log-file writes. EML-processing coverage is organized by outcome:
  `test_eml_happy_paths.py` covers successful workflows,
  `test_eml_fallback_paths.py` covers recoverable inputs that return fallback
  values or diagnostics, and `test_eml_error_paths.py` covers workflows that
  intentionally raise exceptions.
- `tests/tooling/` contains filesystem-backed packaging, release-metadata, and
  TestPyPI candidate-preparation checks. These remain separate from functional
  tests because they validate repository automation rather than EML processing.
- `tests/functional/regressions/` contains original EML files from resolved
  issues. Keep these files byte-for-byte unchanged, protect their checksums in
  the corresponding regression tests, and assert the behavior that previously
  failed.

Run only the filesystem-free unit tests:

```bash
mise run unit
```

Run only the real-file functional tests:

```bash
mise run functional
```

Run only the packaging and release tooling tests:

```bash
mise run tooling
```

To display every collected test name:

```bash
mise run test-verbose
```

## Code Coverage

Run the test suite with branch coverage and enforce the configured 95% minimum:

```bash
mise run coverage
```

The terminal report includes missing line numbers. The run also writes the
standard `.coverage` data file, so normal Coverage.py commands remain
available.

### Generating Coverage Report

After running tests with coverage, generate a text report:

```bash
coverage report
```

### Generating HTML Coverage Report

Run the configured task to produce both terminal and HTML reports:

```bash
mise run coverage-html
```

This will create an `htmlcov/` directory with detailed coverage information. Open `htmlcov/index.html` in your browser to view the interactive coverage report.

You can also regenerate the HTML report from the most recent `.coverage` file:

```bash
coverage html
```

## Continuous Integration

Run every non-mutating quality check locally with:

```bash
mise run quality
mise run pre-commit
```

The pull-request, TestPyPI, and release workflows run formatting, lint, MyPy,
tests, and coverage as sequential check-only commands. The first failure
terminates the quality job; no CI command changes repository files. The
TestPyPI publishing job runs only after its quality-and-package-build job has
succeeded.

Tooling tests include package-installation checks, such as verifying that the
PEP 561 `py.typed` marker is shipped.
