# Enumerations

## Overview

The enumerations module provides various enumeration classes that define constants and type-safe values used throughout the EMLMailReader library. These enumerations improve code readability and prevent invalid value assignments.

## TransferEncoding Enumeration

```python
class TransferEncoding(Enum):
    """
    Enumeration representing different content transfer encoding methods for MIME entities.

    These encoding methods define how binary or non-ASCII content is represented
    in text-based email messages as specified in RFC 2045.
    """
```

### Values

- **`BASE64`** (1): Base64 encoding for binary data and non-ASCII text
- **`SEVEN_BIT`** (2): 7-bit ASCII encoding (default, no encoding needed)
- **`EIGHT_BIT`** (3): 8-bit encoding for extended ASCII characters
- **`QUOTED_PRINTABLE`** (4): Quoted-printable encoding for mostly ASCII text with occasional non-ASCII characters

### Usage Example

```python
from EMLMailReader import TransferEncoding

# Check encoding type
if message.ContentTransferEncoding == TransferEncoding.BASE64:
    print("Content is Base64 encoded")
elif message.ContentTransferEncoding == TransferEncoding.QUOTED_PRINTABLE:
    print("Content is Quoted-Printable encoded")
```

## EntityType Enumeration

```python
class EntityType(Enum):
    """
    Enumeration representing different types of MIME entities found in email messages.

    This classification helps determine how content should be processed and displayed.
    """
```

### Values

- **`ATTACHMENT`** (1): Binary files or documents attached to the email
- **`TEXT`** (2): Plain text or HTML content that forms the email body
- **`MIME_PART`** (3): Container for other MIME parts (multipart entities)

### Usage Example

```python
from EMLMailReader import EntityType

# Process based on entity type
if message.EntityType == EntityType.TEXT:
    print(f"Text content: {message.Body}")
elif message.EntityType == EntityType.ATTACHMENT:
    print("This is an attachment")
elif message.EntityType == EntityType.MIME_PART:
    print("This is a multipart container")
```

## DispositionType Enumeration

```python
class DispositionType(Enum):
    """
    Enumeration representing content disposition types for MIME entities.

    This indicates how the receiving client should handle and display the content.
    """
```

### Values

- **`ATTACHMENT`** (1): Content should be treated as a separate file attachment
- **`INLINE`** (2): Content should be displayed inline within the message body

### Usage Example

```python
from EMLMailReader import DispositionType

# Check how content should be displayed
if attachment.ContentDisposition.DispositionType == DispositionType.INLINE:
    print("Display content inline")
else:
    print("Treat as file attachment")
```

## LoggingLevel Enumeration

```python
class LoggingLevel(Enum):
    """
    Enumeration defining different severity levels for logging messages.

    These levels help categorize log entries by importance and facilitate filtering.
    """
```

### Values

- **`DEBUG`** (1): Detailed diagnostic information for troubleshooting
- **`INFO`** (2): General informational messages about normal operation
- **`ERROR`** (3): Error conditions that don't prevent continued operation
- **`CRITICAL`** (4): Serious errors that may cause the application to terminate

### Usage Example

```python
from EMLMailReader import Logger, LoggingLevel

# Log different types of messages
Logger.logentry("Processing started", LoggingLevel.INFO)
Logger.logentry("Debug information", LoggingLevel.DEBUG)
Logger.logentry("An error occurred", LoggingLevel.ERROR)
```

## LoggingMode Enumeration

```python
class LoggingMode(Enum):
    """
    Enumeration defining different output destinations for logging messages.

    This controls where log messages are written during EML file processing.
    """
```

### Values

- **`CONSOLE`** (1): Log messages are printed to the console/terminal
- **`FILE`** (2): Log messages are written to a log file
- **`NONE`** (3): Logging is disabled (no output generated)

### Usage Example

```python
from EMLMailReader import MailReader, LoggingMode

# Initialize with different logging modes
console_reader = MailReader(logging_mode=LoggingMode.CONSOLE)
file_reader = MailReader(logging_mode=LoggingMode.FILE, TargetLoggingFolder="/logs")
silent_reader = MailReader(logging_mode=LoggingMode.NONE)
```

## Complete Usage Example

```python
from EMLMailReader import (
    MailReader, LoggingMode, LoggingLevel,
    TransferEncoding, EntityType, DispositionType
)

def analyze_email_with_enums(eml_file):
    """Demonstrate usage of all enumerations."""

    # Configure logging
    reader = MailReader(logging_mode=LoggingMode.CONSOLE)
    message = reader.get_email(eml_file)

    if not message:
        return

    # Analyze transfer encoding
    encoding_names = {
        TransferEncoding.BASE64: "Base64",
        TransferEncoding.SEVEN_BIT: "7-bit",
        TransferEncoding.EIGHT_BIT: "8-bit",
        TransferEncoding.QUOTED_PRINTABLE: "Quoted-Printable"
    }

    print(f"Transfer Encoding: {encoding_names.get(message.ContentTransferEncoding, 'Unknown')}")

    # Analyze entity type
    entity_descriptions = {
        EntityType.TEXT: "Text content",
        EntityType.ATTACHMENT: "File attachment",
        EntityType.MIME_PART: "MIME container"
    }

    print(f"Entity Type: {entity_descriptions.get(message.EntityType, 'Unknown')}")

    # Analyze attachments
    for attachment in message.Attachments.export_as_list():
        if attachment.ContentDisposition:
            disposition = attachment.ContentDisposition.DispositionType

            if disposition == DispositionType.INLINE:
                print(f"Attachment '{attachment.Name}' should be displayed inline")
            elif disposition == DispositionType.ATTACHMENT:
                print(f"Attachment '{attachment.Name}' is a separate file")

# Usage
analyze_email_with_enums("/path/to/email.eml")
```

## Related Classes

- [MailReader](MailReader.md) - Uses LoggingMode enumeration
- [RxMailMessage](RxMailMessage.md) - Uses TransferEncoding and EntityType
- [MailAttachment](MailAttachment.md) - Uses DispositionType
- [Logger](Logger.md) - Uses LoggingLevel and LoggingMode
