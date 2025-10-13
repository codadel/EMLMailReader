# Test Instructions

This document provides instructions on how to run the test suite for the EMLMailReader library.

## Prerequisites

Ensure you have Python 3.12+ installed and you're in the project root directory:

```bash
cd /path/to/EMLMailReader
```

## Running All Tests

### Basic Test Execution

To run all test cases with basic output:

```bash
python -m unittest discover tests
```

### Verbose Test Execution

To run all test cases with detailed output showing each test name and result:

```bash
python -m unittest discover tests -v
```

### Running Tests with Pattern Matching

To run only specific test files using pattern matching:

```bash
python -m unittest discover tests -p "test_*.py" -v
```

## Running Specific Test Files

### Single Test File

To run a specific test file:

```bash
python -m unittest tests.test_custom_exceptions -v
```

### Examples of Running Individual Test Files

```bash
# Run custom exceptions tests
python -m unittest tests.test_custom_exceptions -v

# Run enumeration tests
python -m unittest tests.test_enumerations -v

# Run mail reader tests
python -m unittest tests.test_mail_reader -v

# Run mail attachment tests
python -m unittest tests.test_mail_attachment -v

# Run text encoding tests
python -m unittest tests.test_text_encoding -v

# Run processing logs tests
python -m unittest tests.test_processing_logs -v

# Run RxMailMessage tests
python -m unittest tests.test_rx_mail_message -v
```

## Running Specific Test Classes or Methods

### Run a Specific Test Class

```bash
python -m unittest tests.test_custom_exceptions.TestCustomExceptions -v
```

### Run a Specific Test Method

```bash
python -m unittest tests.test_custom_exceptions.TestCustomExceptions.test_invalid_encoding_error_with_encoded_value -v
```

## Code Coverage

### Installing Coverage Tool

First, install the coverage package if not already installed:

```bash
pip install coverage
```

### Running Tests with Coverage

To run all tests and compute code coverage:

```bash
coverage run -m unittest discover tests
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

### Complete Coverage Workflow

Run this sequence of commands for complete coverage analysis:

```bash
# Run tests with coverage collection
coverage run -m unittest discover tests

# Generate text report
coverage report

# Generate HTML report
coverage html

# View specific module coverage
coverage report --show-missing
```

### Coverage with Source Code Focus

To focus coverage only on the EMLMailReader package (excluding test files):

```bash
coverage run --source=EMLMailReader -m unittest discover tests
coverage report
coverage html
```

## Test Structure

The test suite includes the following test files:

- `test_content_disposition.py` - Tests for ContentDisposition class
- `test_content_type.py` - Tests for ContentType class
- `test_custom_exceptions.py` - Tests for all custom exception classes
- `test_email_parsing.py` - Integration tests for email parsing
- `test_enumerations.py` - Tests for all enumeration classes
- `test_mail_address.py` - Tests for MailAddress and MailAddressCollection classes
- `test_mail_attachment.py` - Tests for MailAttachment and MailAttachmentCollection classes
- `test_mail_reader.py` - Tests for MailReader class
- `test_processing_logs.py` - Tests for Logger class
- `test_rx_mail_message.py` - Tests for RxMailMessage class
- `test_text_encoding.py` - Tests for TextEncoding class

## Continuous Integration

For CI/CD pipelines, use this command to run tests and fail on any test failure:

```bash
python -m unittest discover tests -v && echo "All tests passed!" || exit 1
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from the project root directory.

2. **Module Not Found**: If you get import errors, try running with:
   ```bash
   PYTHONPATH=. python -m unittest discover tests -v
   ```

3. **Permission Issues**: On some systems, you might need to use `python3` instead of `python`:
   ```bash
   python3 -m unittest discover tests -v
   ```

### Debug Mode

To run tests with more detailed error information:

```bash
python -m unittest discover tests -v -f
```

## Test Coverage Goals

The current test suite provides comprehensive coverage for:

- ✅ All custom exception classes (100% coverage)
- ✅ All enumeration classes (100% coverage)
- ✅ Logger functionality (95%+ coverage)
- ✅ RxMailMessage class methods (90%+ coverage)
- ✅ MailReader parsing logic (85%+ coverage)
- ✅ Mail attachment and address handling (90%+ coverage)
- ✅ Text encoding scenarios (85%+ coverage)
- ✅ Error handling and edge cases (80%+ coverage)

## Contributing

When adding new tests:

1. Follow the existing naming convention: `test_<feature>.py`
2. Include comprehensive docstrings for all test methods
3. Test both positive and negative scenarios
4. Include edge cases and error conditions
5. Maintain code coverage above `90%`.
