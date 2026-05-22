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
The only current test dependency is `coverage==7.10.7`.

## Running All Tests

Run the configured test task:

```bash
mise run test
```

## Code Coverage

Run the configured coverage task:

```bash
mise run coverage
```

### Generating Coverage Report

After running tests with coverage, generate a text report:

```bash
coverage report
```

### Generating HTML Coverage Report

For a detailed HTML coverage report:

```bash
coverage html
```

This will create an `htmlcov/` directory with detailed coverage information. Open `htmlcov/index.html` in your browser to view the interactive coverage report.


## Continuous Integration

For CI/CD pipelines with mise available, use:

```bash
mise run setup
mise run test
```
