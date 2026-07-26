![EMLMailReader logo](https://static.citadelofcode.com/emlmailreader/logo.png)

![PyPI version](https://img.shields.io/pypi/v/EMLMailReader.svg) ![Static Badge](https://img.shields.io/badge/powered_by-Codadel-orange)

## Overview

EMLMailReader is a comprehensive Python library designed to parse and extract information from EML (Email Message Format) files. The library provides a robust solution for reading email files, extracting headers, body content, attachments, and handling complex MIME structures with support for various encoding formats.

## Key Features

- **Complete EML Parsing**: Parse standard EML files with full MIME support
- **Multi-part Message Support**: Handle complex email structures with nested MIME parts
- **Attachment Extraction**: Extract and save file attachments with proper metadata
- **Encoding Support**: Decode Base64, Quoted-Printable, and other transfer encodings
- **Address Parsing**: Parse and manage email addresses with display names
- **Logging Integration**: Comprehensive logging for debugging and monitoring
- **Exception Handling**: Custom exceptions for specific error scenarios
- **Standards-aware parsing**: Receiver support for RFC 5322, RFC 6854, MIME,
  RFC 2231, RFC 2183, and RFC 6532, with ordered lossless headers and diagnostics

## Quick Start

### Installation

```bash
pip install emlmailreader
```

### Basic Usage

```python
from EMLMailReader import MailReader, LoggingMode

# Initialize the mail reader
reader = MailReader(logging_mode=LoggingMode.CONSOLE)

# Parse an EML file
message = reader.get_email("/path/to/email.eml")

if message:
    # Access basic email information
    print(f"From: {message.From}")
    print(f"Subject: {message.Subject}")
    print(f"Date: {message.Date}")

    # Access recipients
    print(f"To: {message.To}")
    print(f"Cc: {message.Cc}")

    # Access body content
    print(f"Body: {message.Body}")

    # Check for attachments
    if message.Attachments.length() > 0:
        print(f"Found {message.Attachments.length()} attachments")

        # Save attachments to a folder
        message.save_attachments("/path/to/output/folder")

    # Export message as JSON
    json_data = message.export_as_json()
    print(json_data)
```

### Standards-aware usage

```python
from EMLMailReader import MailReader, ParsingMode

# v1 compatibility projections remain enabled by default.
message = MailReader(parsing_mode=ParsingMode.MODERN).get_email("message.eml")

# Ordered, case-insensitive, duplicate-preserving access.
received = message.HeaderFields.get_all("Received")

# Structured address groups, MIME tree, decoded bodies, and diagnostics.
print(message.FromAddresses.to_dict())
print(message.TextBody, message.HtmlBody)
print([diagnostic.to_dict() for diagnostic in message.Diagnostics])

# The old JSON shape remains the default; v2 is the complete structured schema.
legacy_json = message.export_as_json()
structured_json = message.export_as_json(version=2)

# Disable only the v1 projections when corrected modern behavior is required.
modern = MailReader(compatibility_mode=None).get_email("message.eml")
```

## License

This library is distributed under the terms specified in the LICENSE file.

## Support

For issues, questions, or contributions, please refer to the project repository.
