# MailReader

## Overview

The `MailReader` class is the primary entry point for parsing EML (Email Message Format) files. It handles the complete parsing process, including MIME structure analysis, header extraction, content decoding, and attachment processing.

## Class Definition

```python
class MailReader:
    """
    Primary class for parsing and extracting information from EML (email) files.

    This class reads EML files, parses their MIME structure, extracts headers, body content,
    and attachments, then organizes everything into a structured RxMailMessage object.
    Supports multipart messages, various encodings, and comprehensive error handling.
    """
```

## Constructor

### `__init__(self, logging_mode: LoggingMode = LoggingMode.NONE, TargetLoggingFolder: str = str())`

Initializes a new MailReader instance with optional logging configuration.

**Parameters:**
- `logging_mode` (LoggingMode): Logging output mode (CONSOLE, FILE, or NONE)
- `TargetLoggingFolder` (str): Directory path for log files (required when logging_mode is FILE)

**Example:**
```python
from EMLMailReader import MailReader, LoggingMode

# Basic initialization (no logging)
reader = MailReader()

# With console logging
reader = MailReader(logging_mode=LoggingMode.CONSOLE)

# With file logging
reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder="/path/to/logs"
)
```

## Public Methods

### `get_email(self, emlPath: str) -> RxMailMessage | None`

Parses an EML file and returns a structured representation of the email message.

**Parameters:**
- `emlPath` (str): Complete file system path to the EML file to be parsed

**Returns:**
- `RxMailMessage`: Parsed email message object containing all extracted data
- `None`: If parsing fails due to errors

**Raises:**
- `FileMissingError`: When the EML file doesn't exist or isn't accessible
- `InvalidEncodingError`: When unsupported encoding is encountered
- `IncompleteHeaderError`: When malformed headers are found

**Example:**
```python
from EMLMailReader import MailReader, FileMissingError

reader = MailReader()

try:
    # Parse a single EML file
    message = reader.get_email("/path/to/email.eml")

    if message:
        print(f"Subject: {message.Subject}")
        print(f"From: {message.From}")
        print(f"Attachments: {message.Attachments.length()}")
    else:
        print("Failed to parse email")

except FileMissingError:
    print("EML file not found")
except Exception as e:
    print(f"Parsing error: {e}")
```

## Private Methods

The following methods are for internal use only and handle specific aspects of the parsing process:

### `__set_newline_value(self)`

Determines and sets the newline character sequence used in the EML file based on the operating system conventions (\\r\\n, \\r, \\n).

### `__process_mime_entity(self, message: RxMailMessage, ParentBoundary: str) -> RxMailMessage`

Recursively processes individual MIME parts within an email message, handling headers, multipart boundaries, and content extraction.

### `__process_header(self, header: str, message: RxMailMessage) -> None`

Parses individual email headers and populates the appropriate message properties, including standard headers (From, To, Subject) and MIME headers.

### `__get_next_line(self) -> str`

Retrieves the next line from the EML file for processing, managing sequential reading and EOF detection.

### `__get_last_line(self) -> str`

Retrieves the most recently processed line from the EML file for boundary detection and parsing logic.

### `__parse_entity_body(self, message: RxMailMessage, complete_body: str)`

Decodes and processes the body content of a MIME entity based on its transfer encoding (Base64, Quoted-Printable, etc.).

## Usage Examples

### Basic Email Parsing

```python
from EMLMailReader import MailReader

def parse_email(file_path):
    reader = MailReader()
    message = reader.get_email(file_path)

    if message:
        print("=== Email Information ===")
        print(f"From: {message.From}")
        print(f"Subject: {message.Subject}")
        print(f"Date: {message.Date}")
        print(f"Message ID: {message.MessageID}")

        # Recipients
        if message.To.length() > 0:
            print(f"To: {message.To}")
        if message.Cc.length() > 0:
            print(f"Cc: {message.Cc}")

        # Body content
        if message.Body:
            print(f"Body (first 100 chars): {message.Body[:100]}...")

        # Attachments
        print(f"Attachments: {message.Attachments.length()}")

        return message
    else:
        print("Failed to parse email")
        return None

# Usage
email_message = parse_email("/path/to/email.eml")
```

### Batch Processing with Logging

```python
import os
from EMLMailReader import MailReader, LoggingMode

def process_eml_folder(folder_path, output_folder):
    # Setup logging
    log_folder = os.path.join(output_folder, "logs")
    os.makedirs(log_folder, exist_ok=True)

    reader = MailReader(
        logging_mode=LoggingMode.FILE,
        TargetLoggingFolder=log_folder
    )

    # Create attachments folder
    attachments_folder = os.path.join(output_folder, "attachments")
    os.makedirs(attachments_folder, exist_ok=True)

    results = []

    # Process all EML files in folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.eml'):
            file_path = os.path.join(folder_path, filename)

            try:
                message = reader.get_email(file_path)

                if message:
                    # Create folder for this email's attachments
                    email_folder = os.path.join(
                        attachments_folder,
                        f"{filename[:-4]}_attachments"
                    )

                    if message.Attachments.length() > 0:
                        os.makedirs(email_folder, exist_ok=True)
                        message.save_attachments(email_folder)

                    results.append({
                        'file': filename,
                        'subject': message.Subject,
                        'from': str(message.From),
                        'attachments': message.Attachments.length(),
                        'status': 'success'
                    })
                else:
                    results.append({
                        'file': filename,
                        'status': 'failed_to_parse'
                    })

            except Exception as e:
                results.append({
                    'file': filename,
                    'status': f'error: {e}'
                })

    return results

# Usage
results = process_eml_folder("/path/to/eml/files", "/path/to/output")
for result in results:
    print(f"{result['file']}: {result['status']}")
```

### Custom Error Handling

```python
from EMLMailReader import (
    MailReader,
    FileMissingError,
    InvalidEncodingError,
    IncompleteHeaderError,
    FolderNotAvailableError
)

def robust_email_parser(eml_path, output_folder=None):
    reader = MailReader()

    try:
        message = reader.get_email(eml_path)

        if message:
            print(f"✓ Successfully parsed: {eml_path}")

            # Save attachments if output folder provided
            if output_folder and message.Attachments.length() > 0:
                try:
                    message.save_attachments(output_folder)
                    print(f"✓ Saved {message.Attachments.length()} attachments")
                except FolderNotAvailableError:
                    print(f"✗ Output folder not accessible: {output_folder}")

            return message

    except FileMissingError as e:
        print(f"✗ File not found: {eml_path}")
    except InvalidEncodingError as e:
        print(f"✗ Encoding error in: {eml_path}")
    except IncompleteHeaderError as e:
        print(f"✗ Malformed header in: {eml_path}")
    except Exception as e:
        print(f"✗ Unexpected error parsing {eml_path}: {e}")

    return None

# Usage
message = robust_email_parser(
    "/path/to/email.eml",
    "/path/to/attachments"
)
```

## Best Practices

### 1. Always Handle Exceptions

```python
reader = MailReader()

try:
    message = reader.get_email(eml_path)
    # Process message
except Exception as e:
    # Handle errors appropriately
    pass
```

### 2. Use Appropriate Logging

```python
# For development/debugging
reader = MailReader(logging_mode=LoggingMode.CONSOLE)

# For production
reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder="/var/log/emailparser"
)
```

### 3. Check Message Validity

```python
message = reader.get_email(eml_path)
if message:
    # Process valid message
    pass
else:
    # Handle parsing failure
    pass
```

### 4. Resource Management

```python
# The MailReader automatically handles file resources
# No manual cleanup required
reader = MailReader()
message = reader.get_email(eml_path)
# Files are automatically closed
```

## Performance Considerations

- The parser loads the entire EML file into memory for processing
- Large EML files with many attachments may consume significant memory
- Consider processing files individually rather than keeping multiple parsed messages in memory
- Use file logging for production environments to avoid console output overhead

## Related Classes

- [RxMailMessage](RxMailMessage.md) - The parsed email message structure
- [Logger](Logger.md) - Logging configuration and management
- [Exceptions](Exceptions.md) - Error handling classes
