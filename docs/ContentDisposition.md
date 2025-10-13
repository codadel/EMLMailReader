# ContentDisposition

## Overview

The `ContentDisposition` class represents and parses the Content-Disposition header of MIME entities. It indicates how content should be presented (as attachment or inline) and includes metadata such as filename, dates, and size.

## Class Definition

```python
class ContentDisposition:
    """
    A class to represent the Content-Disposition header of a MIME entity.

    This class parses and stores information from the Content-Disposition header,
    which indicates how content should be presented (as attachment or inline)
    and includes metadata such as filename, dates, and size.
    """
```

## Constructor

### `__init__(self)`

Initializes a new ContentDisposition instance with default values.

## Properties

### `DispositionType` (DispositionType)
**Type:** `DispositionType`
**Default:** `DispositionType.ATTACHMENT`
**Description:** Specifies whether the content should be displayed inline or as an attachment.

### `FileName` (str)
**Type:** `str`
**Default:** `""`
**Description:** The suggested filename for the MIME entity when saved to disk.

### `CreationDate` (str)
**Type:** `str`
**Default:** `""`
**Description:** RFC 2822 formatted date when the MIME entity was originally created.

### `ModificationDate` (str)
**Type:** `str`
**Default:** `""`
**Description:** RFC 2822 formatted date when the MIME entity was last modified.

### `Size` (int)
**Type:** `int`
**Default:** `0`
**Description:** Size of the MIME entity content in bytes.

## Public Methods

### `parse(self, ContentDispositionString: str)`

Parses a Content-Disposition header string and populates the object's properties.

**Parameters:**
- `ContentDispositionString` (str): The Content-Disposition header value to parse

**Example:**
```python
from EMLMailReader import ContentDisposition

# Parse basic attachment
disposition = ContentDisposition()
disposition.parse("attachment; filename=document.pdf")
print(f"Type: {disposition.DispositionType.name}")  # ATTACHMENT
print(f"Filename: {disposition.FileName}")          # document.pdf

# Parse with additional metadata
disposition2 = ContentDisposition()
disposition2.parse('attachment; filename="report.xlsx"; size=1024000')
print(f"Filename: {disposition2.FileName}")  # report.xlsx
print(f"Size: {disposition2.Size}")          # 1024000
```

### `__str__(self) -> str`

Returns a JSON string representation of the ContentDisposition object.

**Example:**
```python
disposition = ContentDisposition()
disposition.parse("attachment; filename=test.pdf")
print(str(disposition))  # JSON representation
```

## Usage Examples

### Basic Content Disposition Parsing

```python
from EMLMailReader import ContentDisposition, DispositionType

def parse_disposition_headers():
    """Parse various Content-Disposition headers."""

    test_headers = [
        "attachment",
        "inline",
        "attachment; filename=document.pdf",
        'attachment; filename="my file.txt"',
        "attachment; filename=data.csv; size=2048",
        'inline; filename="image.jpg"; creation-date="Wed, 21 Feb 1996 09:55:06 -0600"'
    ]

    for header in test_headers:
        disposition = ContentDisposition()
        disposition.parse(header)

        print(f"Header: {header}")
        print(f"  Type: {disposition.DispositionType.name}")
        print(f"  Filename: '{disposition.FileName}'")
        print(f"  Size: {disposition.Size}")
        print(f"  Creation Date: '{disposition.CreationDate}'")
        print(f"  Modification Date: '{disposition.ModificationDate}'")
        print()

parse_disposition_headers()
```

## Related Classes

- [DispositionType](Enumerations.md#dispositiontype-enumeration) - Enumeration for disposition types
- [MailAttachment](MailAttachment.md) - Uses ContentDisposition for attachment metadata
- [RxMailMessage](RxMailMessage.md) - Email message parts with ContentDisposition
