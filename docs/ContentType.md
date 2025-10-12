# ContentType

## Overview

The `ContentType` class represents and parses the Content-Type header of MIME entities. It handles the main media type, character encoding, boundary values for multipart content, and name parameters as defined in RFC 2045.

## Class Definition

```python
class ContentType:
    """
    A class to represent the Content-Type header of a MIME entity.

    This class parses and stores information from the Content-Type header,
    including media type, character set, boundary values for multipart content,
    and name parameters as defined in RFC 2045.
    """
```

## Constructor

### `__init__(self)`

Initializes a new ContentType instance with default values.

**Example:**
```python
from EMLMailReader import ContentType

# Create a new content type instance
content_type = ContentType()
print(f"Default media type: {content_type.MediaType}")  # text/plain
print(f"Default charset: {content_type.Charset}")      # us-ascii
```

## Properties

### `MediaType` (str)
**Type:** `str`
**Default:** `"text/plain"`
**Description:** The main media type and subtype (e.g., 'text/plain', 'image/jpeg').

```python
# Access media type
print(f"Media type: {content_type.MediaType}")

# Common media types:
# - text/plain
# - text/html
# - image/jpeg
# - application/pdf
# - multipart/mixed
```

### `Charset` (str)
**Type:** `str`
**Default:** `"us-ascii"`
**Description:** Character encoding used for text content (defaults to US-ASCII per RFC 2045).

```python
# Access charset
print(f"Character set: {content_type.Charset}")

# Common charsets:
# - us-ascii
# - utf-8
# - iso-8859-1
# - windows-1252
```

### `Boundary` (str)
**Type:** `str`
**Default:** `""`
**Description:** Delimiter string used to separate parts in multipart MIME entities.

```python
# Access boundary (for multipart messages)
if content_type.Boundary:
    print(f"Multipart boundary: {content_type.Boundary}")
```

### `Name` (str)
**Type:** `str`
**Default:** `""`
**Description:** Suggested name for the content, often used for attachments.

```python
# Access name parameter
if content_type.Name:
    print(f"Content name: {content_type.Name}")
```

## Public Methods

### `parse(self, ContentTypeString: str = "text/plain; charset=us-ascii")`

Parses a Content-Type header string and populates the object's properties.

**Parameters:**
- `ContentTypeString` (str): The Content-Type header value to parse

**Returns:**
- `None` - modifies the object's properties in place

**Default Behavior:** If no Content-Type is provided or it's invalid, defaults to 'text/plain;charset=us-ascii' as specified in RFC 2045.

**Example:**
```python
from EMLMailReader import ContentType

# Parse simple content type
content_type = ContentType()
content_type.parse("text/html")
print(f"Media type: {content_type.MediaType}")  # text/html
print(f"Charset: {content_type.Charset}")      # us-ascii (default)

# Parse content type with charset
content_type2 = ContentType()
content_type2.parse("text/html; charset=utf-8")
print(f"Media type: {content_type2.MediaType}")  # text/html
print(f"Charset: {content_type2.Charset}")      # utf-8

# Parse multipart content type
content_type3 = ContentType()
content_type3.parse("multipart/mixed; boundary=----=_Part_123")
print(f"Media type: {content_type3.MediaType}")  # multipart/mixed
print(f"Boundary: {content_type3.Boundary}")    # ----=_Part_123

# Parse with name parameter
content_type4 = ContentType()
content_type4.parse('application/pdf; name="document.pdf"')
print(f"Media type: {content_type4.MediaType}")  # application/pdf
print(f"Name: {content_type4.Name}")            # document.pdf
```

### `__str__(self) -> str`

Returns a formatted Content-Type header string representation.

**Returns:**
- `str`: Properly formatted Content-Type header string

**Example:**
```python
content_type = ContentType()
content_type.MediaType = "text/html"
content_type.Charset = "utf-8"
content_type.Name = "webpage.html"

header_string = str(content_type)
print(header_string)  # text/html; charset=utf-8; name=webpage.html
```

## Usage Examples

### Basic Content Type Parsing

```python
from EMLMailReader import ContentType

def parse_content_types():
    """Demonstrate parsing various Content-Type headers."""

    test_headers = [
        "text/plain",
        "text/html; charset=utf-8",
        "image/jpeg",
        "application/pdf; name=document.pdf",
        "multipart/mixed; boundary=----=_Part_123_456",
        "text/plain; charset=iso-8859-1; name=readme.txt",
        "application/octet-stream"
    ]

    for header in test_headers:
        content_type = ContentType()
        content_type.parse(header)

        print(f"Original: {header}")
        print(f"  Media Type: {content_type.MediaType}")
        print(f"  Charset: {content_type.Charset}")
        print(f"  Boundary: {content_type.Boundary or 'None'}")
        print(f"  Name: {content_type.Name or 'None'}")
        print(f"  Reconstructed: {str(content_type)}")
        print()

# Usage
parse_content_types()
```

### Content Type Analysis

```python
from EMLMailReader import MailReader, ContentType

def analyze_message_content_types(eml_file):
    """Analyze Content-Type headers in an email message."""

    reader = MailReader()
    message = reader.get_email(eml_file)

    if not message:
        print("Failed to parse email")
        return

    content_types = []

    def collect_content_types(msg, level=0):
        """Recursively collect content types from message parts."""
        indent = "  " * level

        if msg.ContentType:
            ct = msg.ContentType
            content_types.append(ct)

            print(f"{indent}Content-Type: {ct.MediaType}")
            if ct.Charset != "us-ascii":
                print(f"{indent}  Charset: {ct.Charset}")
            if ct.Boundary:
                print(f"{indent}  Boundary: {ct.Boundary}")
            if ct.Name:
                print(f"{indent}  Name: {ct.Name}")

        # Process child parts
        if hasattr(msg, 'Children'):
            for child in msg.Children:
                collect_content_types(child, level + 1)

    print("Content-Type Analysis:")
    print("=" * 30)
    collect_content_types(message)

    # Summary
    media_types = {}
    charsets = set()

    for ct in content_types:
        main_type = ct.MediaType.split('/')[0] if '/' in ct.MediaType else ct.MediaType
        media_types[main_type] = media_types.get(main_type, 0) + 1
        charsets.add(ct.Charset)

    print(f"\\nSummary:")
    print(f"  Total parts: {len(content_types)}")
    print(f"  Media types: {dict(media_types)}")
    print(f"  Charsets used: {sorted(charsets)}")

    return content_types

# Usage
content_types = analyze_message_content_types("/path/to/email.eml")
```

### Content Type Validation

```python
from EMLMailReader import ContentType
import mimetypes

class ContentTypeValidator:
    """Validate and normalize Content-Type headers."""

    def __init__(self):
        self.valid_charsets = [
            'us-ascii', 'utf-8', 'utf-16', 'utf-32',
            'iso-8859-1', 'iso-8859-15', 'windows-1252',
            'big5', 'gb2312', 'shift_jis', 'euc-jp'
        ]

        self.text_types = ['text/plain', 'text/html', 'text/css', 'text/javascript']
        self.image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp']
        self.application_types = ['application/pdf', 'application/zip', 'application/json']

    def validate_content_type(self, content_type_string):
        """Validate a Content-Type header string."""

        content_type = ContentType()
        content_type.parse(content_type_string)

        issues = []

        # Validate media type format
        if '/' not in content_type.MediaType:
            issues.append("Invalid media type format (missing subtype)")

        # Validate charset for text types
        if content_type.MediaType.startswith('text/'):
            if content_type.Charset.lower() not in [cs.lower() for cs in self.valid_charsets]:
                issues.append(f"Unknown charset: {content_type.Charset}")

        # Check for required boundary in multipart
        if content_type.MediaType.startswith('multipart/'):
            if not content_type.Boundary:
                issues.append("Multipart content type missing boundary parameter")

        # Validate against system MIME types
        try:
            mimetypes.guess_extension(content_type.MediaType)
        except:
            issues.append(f"Unrecognized media type: {content_type.MediaType}")

        return content_type, issues

    def normalize_content_type(self, content_type_string):
        """Normalize Content-Type header to standard format."""

        content_type = ContentType()
        content_type.parse(content_type_string)

        # Normalize media type to lowercase
        content_type.MediaType = content_type.MediaType.lower()

        # Normalize charset
        content_type.Charset = content_type.Charset.lower()

        # Apply common corrections
        if content_type.MediaType == "text" and not content_type.MediaType.endswith("/plain"):
            content_type.MediaType = "text/plain"

        if content_type.Charset in ["ascii", "ansi"]:
            content_type.Charset = "us-ascii"

        return content_type

    def suggest_content_type(self, filename):
        """Suggest Content-Type based on filename."""

        if not filename:
            return ContentType()  # Default

        # Use mimetypes module
        mime_type, encoding = mimetypes.guess_type(filename)

        if mime_type:
            content_type = ContentType()
            content_type.MediaType = mime_type

            # Set appropriate charset for text types
            if mime_type.startswith('text/'):
                content_type.Charset = 'utf-8'  # Modern default

            # Set name parameter
            content_type.Name = filename

            return content_type

        # Fallback to default
        return ContentType()

# Usage examples
def demo_validation():
    validator = ContentTypeValidator()

    # Test validation
    test_headers = [
        "text/html; charset=utf-8",
        "invalid-type",
        "multipart/mixed",  # Missing boundary
        "text/plain; charset=unknown-charset",
        "application/pdf; name=document.pdf"
    ]

    for header in test_headers:
        ct, issues = validator.validate_content_type(header)
        print(f"Header: {header}")
        if issues:
            print(f"  Issues: {', '.join(issues)}")
        else:
            print("  Valid ✓")
        print()

    # Test normalization
    messy_header = "TEXT/HTML; CHARSET=UTF-8"
    normalized = validator.normalize_content_type(messy_header)
    print(f"Original: {messy_header}")
    print(f"Normalized: {str(normalized)}")

    # Test suggestion
    suggested = validator.suggest_content_type("document.pdf")
    print(f"Suggested for 'document.pdf': {str(suggested)}")

demo_validation()
```

### Working with Multipart Content

```python
from EMLMailReader import ContentType
import uuid

class MultipartHelper:
    """Helper class for working with multipart Content-Type headers."""

    @staticmethod
    def create_multipart_content_type(subtype="mixed"):
        """Create a multipart Content-Type with generated boundary."""

        content_type = ContentType()
        content_type.MediaType = f"multipart/{subtype}"

        # Generate unique boundary
        boundary = f"----=_Part_{uuid.uuid4().hex[:16]}"
        content_type.Boundary = boundary

        return content_type

    @staticmethod
    def is_multipart(content_type):
        """Check if Content-Type represents multipart content."""

        if isinstance(content_type, str):
            return content_type.lower().startswith("multipart/")
        elif isinstance(content_type, ContentType):
            return content_type.MediaType.lower().startswith("multipart/")

        return False

    @staticmethod
    def extract_boundary(content_type):
        """Extract boundary from multipart Content-Type."""

        if isinstance(content_type, str):
            ct = ContentType()
            ct.parse(content_type)
            return ct.Boundary
        elif isinstance(content_type, ContentType):
            return content_type.Boundary

        return None

    @staticmethod
    def create_attachment_content_type(filename):
        """Create Content-Type for file attachment."""

        # Guess type from filename
        mime_type, _ = mimetypes.guess_type(filename)

        content_type = ContentType()

        if mime_type:
            content_type.MediaType = mime_type
        else:
            content_type.MediaType = "application/octet-stream"

        content_type.Name = filename

        return content_type

# Usage
def demo_multipart():
    helper = MultipartHelper()

    # Create multipart content type
    multipart_ct = helper.create_multipart_content_type("alternative")
    print(f"Multipart Content-Type: {str(multipart_ct)}")

    # Check if multipart
    print(f"Is multipart: {helper.is_multipart(multipart_ct)}")

    # Extract boundary
    boundary = helper.extract_boundary(multipart_ct)
    print(f"Extracted boundary: {boundary}")

    # Create attachment content type
    attachment_ct = helper.create_attachment_content_type("photo.jpg")
    print(f"Attachment Content-Type: {str(attachment_ct)}")

demo_multipart()
```

### Content Type Conversion and Serialization

```python
from EMLMailReader import ContentType
import json

class ContentTypeSerializer:
    """Serialize and deserialize ContentType objects."""

    @staticmethod
    def to_dict(content_type):
        """Convert ContentType to dictionary."""

        return {
            'media_type': content_type.MediaType,
            'charset': content_type.Charset,
            'boundary': content_type.Boundary,
            'name': content_type.Name
        }

    @staticmethod
    def from_dict(data):
        """Create ContentType from dictionary."""

        content_type = ContentType()
        content_type.MediaType = data.get('media_type', 'text/plain')
        content_type.Charset = data.get('charset', 'us-ascii')
        content_type.Boundary = data.get('boundary', '')
        content_type.Name = data.get('name', '')

        return content_type

    @staticmethod
    def to_json(content_type):
        """Convert ContentType to JSON string."""

        return json.dumps(ContentTypeSerializer.to_dict(content_type))

    @staticmethod
    def from_json(json_string):
        """Create ContentType from JSON string."""

        data = json.loads(json_string)
        return ContentTypeSerializer.from_dict(data)

# Usage
def demo_serialization():
    serializer = ContentTypeSerializer()

    # Create content type
    original = ContentType()
    original.parse("text/html; charset=utf-8; name=page.html")

    # Serialize to JSON
    json_data = serializer.to_json(original)
    print(f"JSON: {json_data}")

    # Deserialize back
    restored = serializer.from_json(json_data)
    print(f"Restored: {str(restored)}")

    # Verify they're equivalent
    print(f"Equivalent: {str(original) == str(restored)}")

demo_serialization()
```

## Best Practices

### 1. Always Use Default Values

```python
# ContentType automatically provides RFC-compliant defaults
content_type = ContentType()
# MediaType = "text/plain", Charset = "us-ascii"
```

### 2. Validate Parsed Content Types

```python
def safe_parse_content_type(header_string):
    """Safely parse Content-Type with validation."""

    content_type = ContentType()

    try:
        content_type.parse(header_string)

        # Basic validation
        if '/' not in content_type.MediaType:
            content_type.MediaType = "text/plain"

        return content_type
    except:
        # Return default on error
        return ContentType()
```

### 3. Handle Character Encoding Properly

```python
def get_effective_charset(content_type):
    """Get the effective character encoding."""

    if content_type.MediaType.startswith('text/'):
        return content_type.Charset or 'us-ascii'
    else:
        return None  # Binary content
```

### 4. Check for Multipart Content

```python
def is_multipart_message(content_type):
    """Check if content type indicates multipart message."""

    return (content_type.MediaType.lower().startswith('multipart/') and
            bool(content_type.Boundary))
```

## Common Content Types

### Text Types
- `text/plain` - Plain text
- `text/html` - HTML content
- `text/css` - CSS stylesheets
- `text/javascript` - JavaScript code

### Image Types
- `image/jpeg` - JPEG images
- `image/png` - PNG images
- `image/gif` - GIF images
- `image/svg+xml` - SVG images

### Application Types
- `application/pdf` - PDF documents
- `application/zip` - ZIP archives
- `application/json` - JSON data
- `application/octet-stream` - Binary data

### Multipart Types
- `multipart/mixed` - Mixed content parts
- `multipart/alternative` - Alternative representations
- `multipart/related` - Related parts (e.g., HTML with images)

## Related Classes

- [ContentDisposition](ContentDisposition.md) - MIME Content-Disposition header handling
- [RxMailMessage](RxMailMessage.md) - Email message using ContentType
- [MailAttachment](MailAttachment.md) - Attachments with ContentType information
- [TextEncoding](TextEncoding.md) - Text encoding utilities
