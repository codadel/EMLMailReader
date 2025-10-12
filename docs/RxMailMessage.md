# RxMailMessage

## Overview

The `RxMailMessage` class is the comprehensive representation of a parsed email message and its MIME structure. This class encapsulates all information extracted from an EML file including headers, body content, attachments, and MIME metadata.

## Class Definition

```python
class RxMailMessage:
    """
    Comprehensive representation of a parsed email message and its MIME structure.

    This class encapsulates all information extracted from an EML file including headers,
    body content, attachments, and MIME metadata. It supports both simple and complex
    multipart email structures with full hierarchical representation of nested MIME parts.
    """
```

## Constructor

### `__init__(self)`

Initializes a new RxMailMessage instance with default values for all properties.

**Example:**
```python
from EMLMailReader import RxMailMessage

# Create a new message instance
message = RxMailMessage()
```

## Properties

### Email Headers

#### `From` (MailAddress | None)
**Type:** `MailAddress` or `None`
**Description:** Sender's email address from the 'From' header.

```python
# Access sender information
if message.From:
    print(f"Sender: {message.From.DisplayName} <{message.From.Email}>")
```

#### `To` (MailAddressCollection)
**Type:** `MailAddressCollection`
**Description:** Collection of recipient email addresses from the 'To' header.

```python
# Access recipients
print(f"Number of recipients: {message.To.length()}")
for address in message.To.export_as_list():
    print(f"To: {address}")
```

#### `Cc` (MailAddressCollection)
**Type:** `MailAddressCollection`
**Description:** Collection of carbon copy recipient addresses from the 'Cc' header.

#### `Bcc` (MailAddressCollection)
**Type:** `MailAddressCollection`
**Description:** Collection of blind carbon copy recipient addresses from the 'Bcc' header.

#### `ReplyTo` (MailAddressCollection)
**Type:** `MailAddressCollection`
**Description:** Collection of reply-to addresses from the 'Reply-To' header.

#### `Subject` (str)
**Type:** `str`
**Description:** Email subject line with decoded content.

```python
print(f"Subject: {message.Subject}")
```

#### `Date` (str)
**Type:** `str`
**Description:** Date and time when the message was sent from the 'Date' header.

#### `MessageID` (str)
**Type:** `str`
**Description:** Unique message identifier from the 'Message-ID' header.

#### `MimeVersion` (str)
**Type:** `str`
**Description:** MIME version specification from the 'MIME-Version' header.

### Content Properties

#### `Body` (str)
**Type:** `str`
**Description:** Decoded text content of the email body.

```python
# Access email body
if message.Body:
    print(f"Body: {message.Body[:200]}...")  # First 200 characters
```

#### `ContentType` (ContentType | None)
**Type:** `ContentType` or `None`
**Description:** MIME Content-Type information for this message part.

```python
# Access content type information
if message.ContentType:
    print(f"Media Type: {message.ContentType.MediaType}")
    print(f"Charset: {message.ContentType.Charset}")
```

#### `ContentDisposition` (ContentDisposition | None)
**Type:** `ContentDisposition` or `None`
**Description:** MIME Content-Disposition information for this message part.

#### `ContentTransferEncoding` (TransferEncoding)
**Type:** `TransferEncoding`
**Description:** Transfer encoding method used for this message part content.

#### `ContentDescription` (str)
**Type:** `str`
**Description:** Textual description of the content from 'Content-Description' header.

#### `ContentID` (str)
**Type:** `str`
**Description:** Unique content identifier for referencing this part from 'Content-ID' header.

### Structure Properties

#### `IsMultiPart` (bool)
**Type:** `bool`
**Description:** Indicates whether this message contains multiple MIME parts.

```python
if message.IsMultiPart:
    print("This is a multipart message")
    print(f"Number of child parts: {len(message.Children)}")
```

#### `Children` (list)
**Type:** `list`
**Description:** List of child MIME parts for multipart messages.

#### `EntityType` (EntityType)
**Type:** `EntityType`
**Description:** Classification of this MIME entity (TEXT, ATTACHMENT, or MIME_PART).

#### `Headers` (dict)
**Type:** `dict`
**Description:** Dictionary of additional headers not handled by specific properties.

```python
# Access custom headers
for header_name, header_value in message.Headers.items():
    print(f"{header_name}: {header_value}")
```

### Attachment Properties

#### `Attachments` (MailAttachmentCollection)
**Type:** `MailAttachmentCollection`
**Description:** Collection of all file attachments found in this message.

```python
# Check for attachments
if message.Attachments.length() > 0:
    print(f"Found {message.Attachments.length()} attachments")

    for attachment in message.Attachments.export_as_list():
        print(f"Attachment: {attachment.Name} ({len(attachment.Contents)} bytes)")
```

## Public Methods

### `export_as_json(self) -> str`

Converts the email message to a JSON string representation.

**Returns:**
- `str`: JSON string containing structured representation of the message

**Example:**
```python
# Export message as JSON
json_data = message.export_as_json()
print(json_data)

# Parse JSON for further processing
import json
message_dict = json.loads(json_data)
print(f"Subject: {message_dict['Subject']}")
print(f"Attachment Count: {message_dict['Attachment-Count']}")
```

### `save_attachments(self, TargetFolderPath: str)`

Saves all email attachments to the specified directory.

**Parameters:**
- `TargetFolderPath` (str): Directory path where attachment files should be saved

**Raises:**
- `FolderNotAvailableError`: If the target directory doesn't exist

**Example:**
```python
import os
from EMLMailReader import FolderNotAvailableError

# Create output directory
output_dir = "/path/to/attachments"
os.makedirs(output_dir, exist_ok=True)

try:
    # Save all attachments
    message.save_attachments(output_dir)
    print(f"Saved {message.Attachments.length()} attachments to {output_dir}")
except FolderNotAvailableError:
    print(f"Directory not accessible: {output_dir}")
```

## Internal Methods

The following methods are used internally during EML parsing and should not be called directly:

### `add_mail_address(self, PropertyName: str, MailAddressValue: str)`

Parses and adds an email address to the specified recipient collection.

### `set_content_type(self, ContentTypeValue: str)`

Parses and sets the Content-Type header for this MIME part.

### `set_content_disposition(self, ContentDispositionValue: str)`

Parses and sets the Content-Disposition header for this MIME part.

### `set_content_transfer_encoding(self, ContentTransferEncodingValue: str)`

Parses and sets the Content-Transfer-Encoding for this MIME part.

### `set_entity_type(self)`

Determines and sets the entity type based on the Content-Type.

## Usage Examples

### Basic Message Information

```python
from EMLMailReader import MailReader

def display_message_info(message):
    """Display basic information about an email message."""

    print("=== EMAIL MESSAGE INFORMATION ===")

    # Basic headers
    print(f"From: {message.From}")
    print(f"Subject: {message.Subject}")
    print(f"Date: {message.Date}")
    print(f"Message ID: {message.MessageID}")

    # Recipients
    if message.To.length() > 0:
        print(f"To: {message.To}")
    if message.Cc.length() > 0:
        print(f"Cc: {message.Cc}")
    if message.Bcc.length() > 0:
        print(f"Bcc: {message.Bcc}")
    if message.ReplyTo.length() > 0:
        print(f"Reply-To: {message.ReplyTo}")

    # Content information
    print(f"MIME Version: {message.MimeVersion}")
    print(f"Is Multipart: {message.IsMultiPart}")
    print(f"Entity Type: {message.EntityType.name}")

    if message.ContentType:
        print(f"Content Type: {message.ContentType.MediaType}")
        print(f"Charset: {message.ContentType.Charset}")

    # Body content
    if message.Body:
        body_preview = message.Body[:200]
        print(f"Body Preview: {body_preview}...")

    # Attachments
    print(f"Attachments: {message.Attachments.length()}")

# Usage
reader = MailReader()
message = reader.get_email("/path/to/email.eml")
if message:
    display_message_info(message)
```

### Working with Multipart Messages

```python
def analyze_multipart_structure(message, level=0):
    """Recursively analyze multipart message structure."""

    indent = "  " * level
    print(f"{indent}MIME Part (Level {level}):")
    print(f"{indent}  Type: {message.EntityType.name}")

    if message.ContentType:
        print(f"{indent}  Content-Type: {message.ContentType.MediaType}")

    if message.IsMultiPart:
        print(f"{indent}  Multipart with {len(message.Children)} children")
        for i, child in enumerate(message.Children):
            print(f"{indent}  Child {i+1}:")
            analyze_multipart_structure(child, level + 1)
    else:
        if message.Body:
            print(f"{indent}  Body Length: {len(message.Body)} characters")
        if message.Attachments.length() > 0:
            print(f"{indent}  Attachments: {message.Attachments.length()}")

# Usage
reader = MailReader()
message = reader.get_email("/path/to/multipart_email.eml")
if message:
    analyze_multipart_structure(message)
```

### Attachment Processing

```python
import os
import mimetypes

def process_attachments(message, output_dir):
    """Process and categorize email attachments."""

    if message.Attachments.length() == 0:
        print("No attachments found")
        return

    # Create categorized folders
    categories = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'other': []
    }

    for category in categories:
        os.makedirs(os.path.join(output_dir, category), exist_ok=True)

    for attachment in message.Attachments.export_as_list():
        print(f"Processing: {attachment.Name}")

        # Determine file extension
        _, ext = os.path.splitext(attachment.Name.lower())

        # Categorize file
        category = 'other'
        for cat, extensions in categories.items():
            if ext in extensions:
                category = cat
                break

        # Save to appropriate folder
        category_dir = os.path.join(output_dir, category)
        file_path = os.path.join(category_dir, attachment.Name)

        with open(file_path, 'wb') as f:
            f.write(attachment.Contents)

        print(f"  Saved to: {category}/{attachment.Name}")
        print(f"  Size: {len(attachment.Contents)} bytes")

        # Display content type information
        if attachment.ContentType:
            print(f"  Content-Type: {attachment.ContentType.MediaType}")

# Usage
reader = MailReader()
message = reader.get_email("/path/to/email_with_attachments.eml")
if message:
    process_attachments(message, "/path/to/output")
```

### JSON Export and Analysis

```python
import json
from datetime import datetime

def export_message_summary(message, output_file):
    """Export message summary with additional analysis."""

    # Get basic JSON export
    basic_json = message.export_as_json()
    message_data = json.loads(basic_json)

    # Add additional analysis
    analysis = {
        'analysis_timestamp': datetime.now().isoformat(),
        'body_length': len(message.Body) if message.Body else 0,
        'has_html_content': 'html' in message.Body.lower() if message.Body else False,
        'multipart_depth': calculate_multipart_depth(message),
        'total_size_estimate': estimate_total_size(message),
        'attachment_details': []
    }

    # Detailed attachment information
    for attachment in message.Attachments.export_as_list():
        attachment_info = {
            'name': attachment.Name,
            'size': len(attachment.Contents),
            'content_type': attachment.ContentType.MediaType if attachment.ContentType else 'unknown',
            'has_content_id': bool(attachment.ContentID)
        }
        analysis['attachment_details'].append(attachment_info)

    # Combine data
    message_data['analysis'] = analysis

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(message_data, f, indent=2, ensure_ascii=False)

    print(f"Message summary exported to: {output_file}")

def calculate_multipart_depth(message, current_depth=0):
    """Calculate the maximum depth of multipart nesting."""
    max_depth = current_depth

    if message.IsMultiPart:
        for child in message.Children:
            child_depth = calculate_multipart_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)

    return max_depth

def estimate_total_size(message):
    """Estimate total message size in bytes."""
    size = 0

    # Body content
    if message.Body:
        size += len(message.Body.encode('utf-8'))

    # Attachments
    for attachment in message.Attachments.export_as_list():
        size += len(attachment.Contents)

    # Child parts
    for child in message.Children:
        size += estimate_total_size(child)

    return size

# Usage
reader = MailReader()
message = reader.get_email("/path/to/email.eml")
if message:
    export_message_summary(message, "/path/to/message_summary.json")
```

## Best Practices

### 1. Always Check for None Values

```python
# Check if From address exists
if message.From:
    sender_email = message.From.Email
else:
    sender_email = "Unknown"

# Check for ContentType
if message.ContentType:
    media_type = message.ContentType.MediaType
else:
    media_type = "text/plain"  # Default
```

### 2. Handle Collections Properly

```python
# Check collection length before iterating
if message.To.length() > 0:
    for recipient in message.To.export_as_list():
        print(recipient.Email)

# Export as list for easier processing
recipients = message.To.export_as_list()
cc_recipients = message.Cc.export_as_list()
all_recipients = recipients + cc_recipients
```

### 3. Safe Attachment Handling

```python
import os

def safe_save_attachments(message, output_dir):
    if message.Attachments.length() == 0:
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for attachment in message.Attachments.export_as_list():
        # Sanitize filename
        safe_name = "".join(c for c in attachment.Name if c.isalnum() or c in (' ', '.', '_', '-'))
        if not safe_name:
            safe_name = f"attachment_{hash(attachment.Contents)}"

        file_path = os.path.join(output_dir, safe_name)

        # Handle duplicate names
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1

        # Save attachment
        with open(file_path, 'wb') as f:
            f.write(attachment.Contents)
```

## Related Classes

- [MailAddress](MailAddress.md) - Individual email address representation
- [MailAddressCollection](MailAddressCollection.md) - Collection of email addresses
- [MailAttachment](MailAttachment.md) - Individual email attachment
- [MailAttachmentCollection](MailAttachmentCollection.md) - Collection of attachments
- [ContentType](ContentType.md) - MIME Content-Type header handling
- [ContentDisposition](ContentDisposition.md) - MIME Content-Disposition header handling
