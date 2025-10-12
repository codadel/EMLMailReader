# MailAttachment

## Overview

The `MailAttachment` class represents a file attachment found in an email message. It encapsulates all information about an email attachment including its content, metadata, and MIME properties required for proper handling and extraction.

## Class Definition

```python
class MailAttachment:
    """
    Represents a file attachment found in an email message.

    This class encapsulates all information about an email attachment including
    its content, metadata, and MIME properties required for proper handling and extraction.
    """
```

## Constructor

### `__init__(self)`

Initializes a new MailAttachment instance with default values.

**Example:**
```python
from EMLMailReader import MailAttachment

# Create a new attachment instance
attachment = MailAttachment()
```

## Properties

### `Name` (str)
**Type:** `str`
**Description:** The filename of the attachment as it should appear when saved.

```python
# Access attachment name
print(f"Attachment name: {attachment.Name}")
```

### `ContentType` (ContentType)
**Type:** `ContentType`
**Description:** MIME Content-Type information including media type and parameters.

```python
# Access content type information
if attachment.ContentType:
    print(f"Media type: {attachment.ContentType.MediaType}")
    print(f"Charset: {attachment.ContentType.Charset}")
```

### `ContentDisposition` (ContentDisposition)
**Type:** `ContentDisposition`
**Description:** Content-Disposition header information including disposition type and metadata.

```python
# Access disposition information
if attachment.ContentDisposition:
    print(f"Disposition: {attachment.ContentDisposition.DispositionType.name}")
    print(f"Filename: {attachment.ContentDisposition.FileName}")
```

### `Contents` (bytes)
**Type:** `bytes`
**Description:** The actual binary content of the attachment file.

```python
# Access attachment contents
print(f"Attachment size: {len(attachment.Contents)} bytes")

# Save attachment to file
with open(attachment.Name, 'wb') as f:
    f.write(attachment.Contents)
```

### `ContentID` (str)
**Type:** `str`
**Description:** Unique identifier for the attachment, used for referencing in HTML content.

```python
# Check if attachment is referenced in email body
if attachment.ContentID:
    print(f"Content ID: {attachment.ContentID}")
    # This attachment might be embedded in HTML content
```

## Public Methods

### `parse_values(self, contents: bytes, content_type: ContentType, content_disposition: ContentDisposition, content_id: str)`

Initializes the MailAttachment object with provided content and metadata.

**Parameters:**
- `contents` (bytes): Binary content of the attachment file
- `content_type` (ContentType): Parsed Content-Type header information
- `content_disposition` (ContentDisposition): Parsed Content-Disposition header information
- `content_id` (str): Content-ID value for referencing the attachment

**Returns:**
- `None` - modifies the object's properties in place

**Note:** This method is typically called internally during email parsing.

**Example:**
```python
from EMLMailReader import MailAttachment, ContentType, ContentDisposition

# Create attachment with specific content
attachment = MailAttachment()

# Create content type
content_type = ContentType()
content_type.parse("image/jpeg; name=photo.jpg")

# Create content disposition
content_disposition = ContentDisposition()
content_disposition.parse("attachment; filename=photo.jpg")

# Binary content (example)
binary_content = b"\\xff\\xd8\\xff\\xe0..."  # JPEG header

# Initialize attachment
attachment.parse_values(
    contents=binary_content,
    content_type=content_type,
    content_disposition=content_disposition,
    content_id="photo@email.com"
)

print(f"Attachment: {attachment.Name}")
```

## Usage Examples

### Basic Attachment Handling

```python
from EMLMailReader import MailReader
import os

def extract_attachments(eml_file, output_dir):
    """Extract all attachments from an EML file."""

    reader = MailReader()
    message = reader.get_email(eml_file)

    if not message:
        print("Failed to parse email")
        return []

    if message.Attachments.length() == 0:
        print("No attachments found")
        return []

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    extracted_files = []

    for attachment in message.Attachments.export_as_list():
        # Generate safe filename
        safe_name = attachment.Name if attachment.Name else "unnamed_attachment"
        file_path = os.path.join(output_dir, safe_name)

        # Handle duplicate filenames
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1

        # Save attachment
        with open(file_path, 'wb') as f:
            f.write(attachment.Contents)

        extracted_files.append({
            'name': attachment.Name,
            'path': file_path,
            'size': len(attachment.Contents),
            'content_type': attachment.ContentType.MediaType if attachment.ContentType else 'unknown'
        })

        print(f"Extracted: {attachment.Name} ({len(attachment.Contents)} bytes)")

    return extracted_files

# Usage
files = extract_attachments("/path/to/email.eml", "/path/to/output")
```

### Attachment Analysis

```python
from EMLMailReader import MailReader
import mimetypes

def analyze_attachments(eml_file):
    """Analyze attachments in an email message."""

    reader = MailReader()
    message = reader.get_email(eml_file)

    if not message or message.Attachments.length() == 0:
        print("No attachments to analyze")
        return

    print(f"Found {message.Attachments.length()} attachments:")
    print("=" * 50)

    total_size = 0
    file_types = {}

    for i, attachment in enumerate(message.Attachments.export_as_list(), 1):
        print(f"\\nAttachment {i}:")
        print(f"  Name: {attachment.Name}")
        print(f"  Size: {len(attachment.Contents):,} bytes")

        # Content type analysis
        if attachment.ContentType:
            media_type = attachment.ContentType.MediaType
            print(f"  Content-Type: {media_type}")

            # Track file types
            main_type = media_type.split('/')[0] if '/' in media_type else media_type
            file_types[main_type] = file_types.get(main_type, 0) + 1

        # Content disposition
        if attachment.ContentDisposition:
            print(f"  Disposition: {attachment.ContentDisposition.DispositionType.name}")
            if attachment.ContentDisposition.FileName:
                print(f"  Original filename: {attachment.ContentDisposition.FileName}")

        # Content ID (for embedded content)
        if attachment.ContentID:
            print(f"  Content-ID: {attachment.ContentID}")
            print("  (This attachment may be embedded in email content)")

        # File extension analysis
        if attachment.Name:
            _, ext = os.path.splitext(attachment.Name.lower())
            if ext:
                mime_type, _ = mimetypes.guess_type(attachment.Name)
                if mime_type:
                    print(f"  Detected MIME type: {mime_type}")

        total_size += len(attachment.Contents)

    # Summary
    print(f"\\nSummary:")
    print(f"  Total attachments: {message.Attachments.length()}")
    print(f"  Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    print(f"  File types: {dict(file_types)}")

# Usage
analyze_attachments("/path/to/email.eml")
```

### Attachment Filtering and Categorization

```python
import os
from EMLMailReader import MailReader

class AttachmentProcessor:
    """Advanced attachment processing with filtering and categorization."""

    def __init__(self):
        self.file_categories = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'executables': ['.exe', '.msi', '.app', '.deb', '.rpm'],
            'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg']
        }

    def categorize_attachment(self, attachment):
        """Categorize attachment by file extension."""
        if not attachment.Name:
            return 'unknown'

        _, ext = os.path.splitext(attachment.Name.lower())

        for category, extensions in self.file_categories.items():
            if ext in extensions:
                return category

        return 'other'

    def is_safe_attachment(self, attachment):
        """Check if attachment is considered safe."""
        if not attachment.Name:
            return False

        # Check for dangerous extensions
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
        _, ext = os.path.splitext(attachment.Name.lower())

        if ext in dangerous_extensions:
            return False

        # Check file size (reject files larger than 50MB)
        if len(attachment.Contents) > 50 * 1024 * 1024:
            return False

        return True

    def extract_by_category(self, eml_file, output_dir, allowed_categories=None):
        """Extract attachments filtered by category."""

        reader = MailReader()
        message = reader.get_email(eml_file)

        if not message or message.Attachments.length() == 0:
            return {}

        # Create category directories
        extracted = {}

        for attachment in message.Attachments.export_as_list():
            category = self.categorize_attachment(attachment)

            # Filter by allowed categories
            if allowed_categories and category not in allowed_categories:
                continue

            # Safety check
            if not self.is_safe_attachment(attachment):
                print(f"Skipping potentially unsafe attachment: {attachment.Name}")
                continue

            # Create category directory
            category_dir = os.path.join(output_dir, category)
            os.makedirs(category_dir, exist_ok=True)

            # Save attachment
            file_path = os.path.join(category_dir, attachment.Name)

            # Handle duplicates
            counter = 1
            original_path = file_path
            while os.path.exists(file_path):
                name, ext = os.path.splitext(original_path)
                file_path = f"{name}_{counter}{ext}"
                counter += 1

            with open(file_path, 'wb') as f:
                f.write(attachment.Contents)

            # Track extracted files
            if category not in extracted:
                extracted[category] = []

            extracted[category].append({
                'name': attachment.Name,
                'path': file_path,
                'size': len(attachment.Contents)
            })

        return extracted

    def generate_report(self, eml_file):
        """Generate detailed attachment report."""

        reader = MailReader()
        message = reader.get_email(eml_file)

        if not message:
            return None

        report = {
            'email_file': eml_file,
            'total_attachments': message.Attachments.length(),
            'categories': {},
            'safety_issues': [],
            'embedded_content': [],
            'total_size': 0
        }

        for attachment in message.Attachments.export_as_list():
            category = self.categorize_attachment(attachment)
            size = len(attachment.Contents)

            # Update category stats
            if category not in report['categories']:
                report['categories'][category] = {'count': 0, 'size': 0, 'files': []}

            report['categories'][category]['count'] += 1
            report['categories'][category]['size'] += size
            report['categories'][category]['files'].append(attachment.Name)

            # Check for safety issues
            if not self.is_safe_attachment(attachment):
                report['safety_issues'].append(attachment.Name)

            # Check for embedded content
            if attachment.ContentID:
                report['embedded_content'].append({
                    'name': attachment.Name,
                    'content_id': attachment.ContentID
                })

            report['total_size'] += size

        return report

# Usage examples
def demo_attachment_processing():
    processor = AttachmentProcessor()

    # Extract only images and documents
    extracted = processor.extract_by_category(
        "/path/to/email.eml",
        "/path/to/output",
        allowed_categories=['images', 'documents']
    )

    print("Extracted files by category:")
    for category, files in extracted.items():
        print(f"  {category}: {len(files)} files")

    # Generate detailed report
    report = processor.generate_report("/path/to/email.eml")
    if report:
        print(f"\\nAttachment Report:")
        print(f"  Total attachments: {report['total_attachments']}")
        print(f"  Total size: {report['total_size']:,} bytes")
        print(f"  Categories: {list(report['categories'].keys())}")

        if report['safety_issues']:
            print(f"  Safety issues: {len(report['safety_issues'])} files")

        if report['embedded_content']:
            print(f"  Embedded content: {len(report['embedded_content'])} files")

demo_attachment_processing()
```

### Working with Embedded Content

```python
from EMLMailReader import MailReader
import re

def extract_embedded_images(eml_file, output_dir):
    """Extract images that are embedded in HTML email content."""

    reader = MailReader()
    message = reader.get_email(eml_file)

    if not message:
        return []

    # Find Content-IDs referenced in HTML body
    referenced_cids = set()
    if message.Body and 'cid:' in message.Body:
        # Find all cid: references in HTML
        cid_pattern = r'cid:([^"\\s>]+)'
        matches = re.findall(cid_pattern, message.Body)
        referenced_cids.update(matches)

    extracted_embedded = []
    os.makedirs(output_dir, exist_ok=True)

    for attachment in message.Attachments.export_as_list():
        # Check if this attachment is embedded content
        if attachment.ContentID:
            # Remove angle brackets if present
            clean_cid = attachment.ContentID.strip('<>')

            is_referenced = clean_cid in referenced_cids

            # Save embedded image
            filename = attachment.Name if attachment.Name else f"embedded_{clean_cid}"
            file_path = os.path.join(output_dir, filename)

            with open(file_path, 'wb') as f:
                f.write(attachment.Contents)

            extracted_embedded.append({
                'name': attachment.Name,
                'content_id': attachment.ContentID,
                'path': file_path,
                'size': len(attachment.Contents),
                'referenced_in_html': is_referenced
            })

            print(f"Extracted embedded content: {filename}")
            print(f"  Content-ID: {attachment.ContentID}")
            print(f"  Referenced in HTML: {is_referenced}")

    return extracted_embedded

# Usage
embedded_files = extract_embedded_images("/path/to/html_email.eml", "/path/to/embedded")
```

## Best Practices

### 1. Always Check for Valid Content

```python
def safe_save_attachment(attachment, output_path):
    """Safely save an attachment with validation."""

    # Check if attachment has content
    if not attachment.Contents:
        print("Attachment has no content")
        return False

    # Check if filename is valid
    if not attachment.Name:
        print("Attachment has no filename")
        return False

    # Sanitize filename
    safe_filename = "".join(c for c in attachment.Name if c.isalnum() or c in (' ', '.', '_', '-'))

    try:
        with open(os.path.join(output_path, safe_filename), 'wb') as f:
            f.write(attachment.Contents)
        return True
    except Exception as e:
        print(f"Error saving attachment: {e}")
        return False
```

### 2. Handle Large Attachments Carefully

```python
def check_attachment_size(attachment, max_size_mb=50):
    """Check if attachment size is within limits."""

    size_bytes = len(attachment.Contents)
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > max_size_mb:
        print(f"Warning: Large attachment {attachment.Name} ({size_mb:.2f} MB)")
        return False

    return True
```

### 3. Verify Content Type

```python
import mimetypes

def verify_content_type(attachment):
    """Verify attachment content type matches filename."""

    if not attachment.Name or not attachment.ContentType:
        return True  # Can't verify

    # Guess MIME type from filename
    guessed_type, _ = mimetypes.guess_type(attachment.Name)
    declared_type = attachment.ContentType.MediaType

    if guessed_type and guessed_type != declared_type:
        print(f"Content type mismatch for {attachment.Name}")
        print(f"  Declared: {declared_type}")
        print(f"  Expected: {guessed_type}")
        return False

    return True
```

## Related Classes

- [MailAttachmentCollection](MailAttachmentCollection.md) - Collection of MailAttachment instances
- [ContentType](ContentType.md) - MIME Content-Type header handling
- [ContentDisposition](ContentDisposition.md) - MIME Content-Disposition header handling
- [RxMailMessage](RxMailMessage.md) - Email message containing attachments
