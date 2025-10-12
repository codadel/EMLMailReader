# Exceptions

## Overview

The EMLMailReader library provides custom exception classes for specific error scenarios that can occur during email parsing. These exceptions provide detailed information about parsing failures and help developers handle different error conditions appropriately.

## Exception Classes

## InvalidEncodingError

```python
class InvalidEncodingError(Exception):
    """
    A custom exception class to report invalid or unsupported text encoding errors.

    This exception is raised when the library encounters an encoding type that
    is not supported or when decoding fails due to invalid encoded content.
    """
```

### Properties
- **`EncodedValue`** (str): The invalid encoded string that caused the error
- **`Message`** (str): Descriptive error message

### Usage Example

```python
from EMLMailReader import MailReader, InvalidEncodingError

try:
    reader = MailReader()
    message = reader.get_email("/path/to/email.eml")
except InvalidEncodingError as e:
    print(f"Encoding error: {e}")
    print(f"Problematic content: {e.EncodedValue}")
```

## FileMissingError

```python
class FileMissingError(Exception):
    """
    A custom exception class to report when a required file is missing or inaccessible.

    This exception is raised when attempting to read an EML file that doesn't exist
    at the specified path or when file access permissions are insufficient.
    """
```

### Properties
- **`filePath`** (str): The file path that was not found or is inaccessible

### Usage Example

```python
from EMLMailReader import MailReader, FileMissingError

try:
    reader = MailReader()
    message = reader.get_email("/nonexistent/email.eml")
except FileMissingError as e:
    print(f"File not found: {e.filePath}")
```

## IncompleteHeaderError

```python
class IncompleteHeaderError(Exception):
    """
    A custom exception to report malformed or incomplete email headers in EML files.

    This exception is raised when a header line is found that doesn't conform to
    the expected format (missing colon separator, continuation without initial header, etc.).
    """
```

### Properties
- **`InvalidHeaderValue`** (str): The malformed header content that caused the error
- **`LineInFile`** (int): The line number in the EML file where the error occurred

### Usage Example

```python
from EMLMailReader import MailReader, IncompleteHeaderError

try:
    reader = MailReader()
    message = reader.get_email("/path/to/malformed_email.eml")
except IncompleteHeaderError as e:
    print(f"Malformed header on line {e.LineInFile}: {e.InvalidHeaderValue}")
```

## FolderNotAvailableError

```python
class FolderNotAvailableError(Exception):
    """
    A custom exception class to report when a required directory is missing or inaccessible.

    This exception is raised when attempting to access a folder that doesn't exist
    or when directory access permissions are insufficient for operations like saving attachments.
    """
```

### Properties
- **`folderPath`** (str): The folder path that was not found or is inaccessible

### Usage Example

```python
from EMLMailReader import RxMailMessage, FolderNotAvailableError

try:
    message = get_parsed_message()  # Assume we have a message
    message.save_attachments("/nonexistent/folder")
except FolderNotAvailableError as e:
    print(f"Folder not accessible: {e.folderPath}")
```

## InvalidPropertyError

```python
class InvalidPropertyError(Exception):
    """
    A custom exception class to report when an invalid or unsupported property is accessed.

    This exception is raised when attempting to set or access properties that don't exist
    on an object or when property values don't meet validation requirements.
    """
```

### Properties
- **`property_name`** (str): The name of the invalid property that was accessed

### Usage Example

```python
from EMLMailReader import InvalidPropertyError

try:
    # Some operation that might access invalid property
    pass
except InvalidPropertyError as e:
    print(f"Invalid property: {e.property_name}")
```

## Comprehensive Error Handling Example

```python
from EMLMailReader import (
    MailReader, LoggingMode,
    FileMissingError, InvalidEncodingError, IncompleteHeaderError,
    FolderNotAvailableError, InvalidPropertyError
)
import os

def robust_email_processor(eml_file, output_folder=None):
    """
    Process an EML file with comprehensive error handling.
    """

    try:
        # Initialize reader with logging
        reader = MailReader(logging_mode=LoggingMode.CONSOLE)

        # Parse the email
        message = reader.get_email(eml_file)

        if message:
            print(f"✓ Successfully parsed: {os.path.basename(eml_file)}")
            print(f"  Subject: {message.Subject}")
            print(f"  From: {message.From}")
            print(f"  Attachments: {message.Attachments.length()}")

            # Try to save attachments if output folder specified
            if output_folder and message.Attachments.length() > 0:
                try:
                    # Ensure output folder exists
                    os.makedirs(output_folder, exist_ok=True)
                    message.save_attachments(output_folder)
                    print(f"✓ Saved {message.Attachments.length()} attachments to {output_folder}")

                except FolderNotAvailableError as e:
                    print(f"✗ Cannot access output folder: {e.folderPath}")
                    return None

            return message
        else:
            print(f"✗ Failed to parse {eml_file} (unknown error)")
            return None

    except FileMissingError as e:
        print(f"✗ File not found: {e.filePath}")
        print("  Please check the file path and permissions")

    except InvalidEncodingError as e:
        print(f"✗ Encoding error in: {eml_file}")
        print(f"  Problem with encoded content: {e.EncodedValue[:50]}...")
        print("  The email may contain unsupported character encoding")

    except IncompleteHeaderError as e:
        print(f"✗ Malformed email headers in: {eml_file}")
        print(f"  Invalid header on line {e.LineInFile}: {e.InvalidHeaderValue}")
        print("  The email file may be corrupted or non-standard")

    except InvalidPropertyError as e:
        print(f"✗ Internal error - invalid property: {e.property_name}")
        print("  This may indicate a bug in the library")

    except Exception as e:
        print(f"✗ Unexpected error processing {eml_file}: {e}")
        print("  This is an unhandled error type")

    return None

# Batch processing with error handling
def process_email_batch(eml_files, output_base_folder):
    """
    Process multiple EML files with individual error handling.
    """

    results = {
        'successful': [],
        'failed': [],
        'errors': {}
    }

    for eml_file in eml_files:
        try:
            # Create individual output folder for each email
            filename = os.path.splitext(os.path.basename(eml_file))[0]
            email_output_folder = os.path.join(output_base_folder, filename)

            message = robust_email_processor(eml_file, email_output_folder)

            if message:
                results['successful'].append(eml_file)
            else:
                results['failed'].append(eml_file)

        except Exception as e:
            results['failed'].append(eml_file)
            results['errors'][eml_file] = str(e)

    # Print summary
    print(f"\\n=== Processing Summary ===")
    print(f"Successful: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['errors']:
        print("\\nErrors encountered:")
        for file, error in results['errors'].items():
            print(f"  {os.path.basename(file)}: {error}")

    return results

# Usage examples
if __name__ == "__main__":
    # Single file processing
    message = robust_email_processor(
        "/path/to/email.eml",
        "/path/to/output"
    )

    # Batch processing
    email_files = [
        "/path/to/email1.eml",
        "/path/to/email2.eml",
        "/path/to/email3.eml"
    ]

    results = process_email_batch(email_files, "/path/to/batch_output")
```

## Error Prevention Best Practices

### 1. Always Check File Existence

```python
import os
from EMLMailReader import MailReader, FileMissingError

def safe_email_parsing(eml_path):
    if not os.path.exists(eml_path):
        print(f"File does not exist: {eml_path}")
        return None

    if not os.access(eml_path, os.R_OK):
        print(f"File is not readable: {eml_path}")
        return None

    try:
        reader = MailReader()
        return reader.get_email(eml_path)
    except FileMissingError:
        # This shouldn't happen after our checks, but just in case
        print(f"Unexpected file access error: {eml_path}")
        return None
```

### 2. Validate Output Directories

```python
import os
from EMLMailReader import FolderNotAvailableError

def safe_attachment_saving(message, output_dir):
    try:
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Check if directory is writable
        if not os.access(output_dir, os.W_OK):
            print(f"Directory is not writable: {output_dir}")
            return False

        message.save_attachments(output_dir)
        return True

    except FolderNotAvailableError as e:
        print(f"Cannot access folder: {e.folderPath}")
        return False
```

### 3. Handle Encoding Issues Gracefully

```python
from EMLMailReader import MailReader, InvalidEncodingError

def tolerant_email_parsing(eml_path):
    try:
        reader = MailReader()
        message = reader.get_email(eml_path)
        return message, None

    except InvalidEncodingError as e:
        print(f"Encoding issue detected, trying fallback methods...")
        # Could implement fallback parsing strategies here
        return None, f"Encoding error: {e.EncodedValue[:50]}..."
```

## Related Classes

- [MailReader](MailReader.md) - May raise FileMissingError, InvalidEncodingError, IncompleteHeaderError
- [RxMailMessage](RxMailMessage.md) - save_attachments() may raise FolderNotAvailableError
- [Logger](Logger.md) - May raise FolderNotAvailableError for file logging
