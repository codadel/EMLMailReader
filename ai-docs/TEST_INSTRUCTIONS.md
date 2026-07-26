# Test Instructions

This document provides instructions on how to run the test suite for the EMLMailReader library.

## Prerequisites

The recommended local workflow uses [mise](https://mise.jdx.dev/) with the
project's `mise.toml`. Mise will install/use Python 3.12 and create a local
`.venv` automatically.

Start from the project root:

```bash
cd /path/to/EMLMailReader
```

Install the local package and project test requirements:

```bash
mise run setup
```

This installs the package in editable mode and installs `requirements.txt`.
The test toolchain uses:

- `pytest` as the test runner. It discovers the existing `unittest.TestCase`
  suite without requiring a rewrite.
- `pytest-cov` as the Coverage.py integration.
- `coverage` for persisted `.coverage` data and terminal or HTML reports.

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
  and log-file writes.
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

For CI/CD pipelines with mise available, use:

```bash
mise run setup
mise run test
```

The release workflow invokes the same pytest configuration with:

```bash
python -m pytest
```
