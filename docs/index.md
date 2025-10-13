# EMLMailReader

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

### Advanced Usage with Logging

```python
from EMLMailReader import MailReader, LoggingMode
import os

# Create a logs directory
logs_dir = "/path/to/logs"
os.makedirs(logs_dir, exist_ok=True)

# Initialize reader with file logging
reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder=logs_dir
)

# Parse multiple EML files
eml_files = ["/path/to/email1.eml", "/path/to/email2.eml"]

for eml_file in eml_files:
    try:
        message = reader.get_email(eml_file)
        if message:
            print(f"Successfully parsed: {eml_file}")
            print(f"Subject: {message.Subject}")
    except Exception as e:
        print(f"Failed to parse {eml_file}: {e}")
```

## Architecture

The library is organized into several key components:

1. **Core Parser** (`MailReader`): Main entry point for parsing EML files
2. **Message Representation** (`RxMailMessage`): Complete email message structure
3. **Address Handling** (`MailAddress`, `MailAddressCollection`): Email address parsing and management
4. **Attachment Support** (`MailAttachment`, `MailAttachmentCollection`): File attachment handling
5. **MIME Headers** (`ContentType`, `ContentDisposition`): MIME header parsing
6. **Encoding Support** (`TextEncoding`): Text and binary content decoding
7. **Utilities** (`Logger`, Enumerations, Exceptions): Supporting infrastructure

## Library Classes

### Core Classes
- [**MailReader**](MailReader.md) - Primary EML file parser
- [**RxMailMessage**](RxMailMessage.md) - Complete email message representation

### Address and Attachment Classes
- [**MailAddress**](MailAddress.md) - Individual email address representation
- [**MailAddressCollection**](MailAddressCollection.md) - Collection of email addresses
- [**MailAttachment**](MailAttachment.md) - Individual email attachment
- [**MailAttachmentCollection**](MailAttachmentCollection.md) - Collection of attachments

### MIME Header Classes
- [**ContentType**](ContentType.md) - MIME Content-Type header handling
- [**ContentDisposition**](ContentDisposition.md) - MIME Content-Disposition header handling

### Utility Classes
- [**TextEncoding**](TextEncoding.md) - Text encoding and decoding utilities
- [**Logger**](Logger.md) - Logging configuration and management

### Supporting Classes
- [**Enumerations**](Enumerations.md) - Library enumerations and constants
- [**Exceptions**](Exceptions.md) - Library-specific exception classes

## Error Handling

The library provides comprehensive error handling through custom exceptions:

```python
from EMLMailReader import MailReader, FileMissingError, InvalidEncodingError

reader = MailReader()

try:
    message = reader.get_email("/path/to/email.eml")
except FileMissingError as e:
    print(f"File not found: {e}")
except InvalidEncodingError as e:
    print(f"Encoding error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

## Requirements

- Python 3.12+
- Standard library modules: `os`, `json`, `logging`, `datetime`, `base64`, `quopri`, `enum`, `copy`
