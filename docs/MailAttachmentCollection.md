# MailAttachmentCollection

## Overview

The `MailAttachmentCollection` class provides a container for managing multiple `MailAttachment` instances. It facilitates storage, access, and manipulation of email attachments found within an email message, enabling batch operations and organized attachment handling.

## Class Definition

```python
class MailAttachmentCollection:
    """
    A collection class to manage multiple MailAttachment instances.

    This class provides a container for storing and manipulating lists of email attachments
    found within an email message, facilitating batch operations and iteration.
    """
```

## Constructor

### `__init__(self)`

Initializes a new empty MailAttachmentCollection instance.

**Example:**
```python
from EMLMailReader import MailAttachmentCollection

# Create a new attachment collection
attachments = MailAttachmentCollection()
```

## Properties

### `__attachments` (list[MailAttachment])
**Type:** `list[MailAttachment]` (private)
**Description:** Internal list containing MailAttachment instances in the collection. This property is private and should not be accessed directly.

## Public Methods

### `append(self, attachment: MailAttachment)`

Adds a MailAttachment instance to the end of the collection.

**Parameters:**
- `attachment` (MailAttachment): MailAttachment object to be added to the collection

**Returns:**
- `None` - modifies the collection in place

**Example:**
```python
from EMLMailReader import MailAttachment, MailAttachmentCollection

# Create collection and attachment
collection = MailAttachmentCollection()
attachment = MailAttachment()

# Set attachment properties
attachment.Name = "document.pdf"
attachment.Contents = b"PDF content here..."

# Add to collection
collection.append(attachment)
print(f"Collection now has {collection.length()} attachments")
```

### `length(self) -> int`

Returns the number of MailAttachment items in the collection.

**Returns:**
- `int`: Count of MailAttachment instances in the collection

**Example:**
```python
collection = MailAttachmentCollection()
print(f"Empty collection length: {collection.length()}")  # 0

# After adding attachments
print(f"Collection length: {collection.length()}")
```

### `export_as_list(self) -> list`

Exports the collection as a new list of MailAttachment instances.

**Returns:**
- `list`: A new list containing deep copies of all MailAttachment instances

**Note:** This method creates deep copies to prevent external modification of the collection's internal state.

**Example:**
```python
# Export attachments for processing
attachment_list = collection.export_as_list()

for attachment in attachment_list:
    print(f"Attachment: {attachment.Name}")
    print(f"Size: {len(attachment.Contents)} bytes")
```

## Usage Examples

### Basic Collection Operations

```python
from EMLMailReader import MailReader
import os

def process_email_attachments(eml_file):
    """Process all attachments in an email message."""

    reader = MailReader()
    message = reader.get_email(eml_file)

    if not message:
        print("Failed to parse email")
        return

    attachments = message.Attachments

    print(f"Email has {attachments.length()} attachments")

    if attachments.length() > 0:
        print("\\nAttachment details:")

        for i, attachment in enumerate(attachments.export_as_list(), 1):
            print(f"{i}. {attachment.Name}")
            print(f"   Size: {len(attachment.Contents):,} bytes")

            if attachment.ContentType:
                print(f"   Type: {attachment.ContentType.MediaType}")

            if attachment.ContentID:
                print(f"   Content-ID: {attachment.ContentID}")

    return attachments

# Usage
attachments = process_email_attachments("/path/to/email.eml")
```

### Batch Attachment Processing

```python
from EMLMailReader import MailReader, MailAttachmentCollection
import os
import shutil

class AttachmentBatchProcessor:
    """Process multiple email attachments in batch operations."""

    def __init__(self, output_base_dir):
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)

    def extract_all_attachments(self, eml_files):
        """Extract attachments from multiple EML files."""

        all_attachments = MailAttachmentCollection()
        extraction_log = []

        for eml_file in eml_files:
            try:
                reader = MailReader()
                message = reader.get_email(eml_file)

                if message and message.Attachments.length() > 0:
                    # Create subdirectory for this email
                    email_name = os.path.splitext(os.path.basename(eml_file))[0]
                    email_dir = os.path.join(self.output_base_dir, email_name)
                    os.makedirs(email_dir, exist_ok=True)

                    # Process each attachment
                    for attachment in message.Attachments.export_as_list():
                        # Add to master collection
                        all_attachments.append(attachment)

                        # Save attachment
                        file_path = os.path.join(email_dir, attachment.Name or "unnamed")

                        # Handle duplicate names
                        counter = 1
                        original_path = file_path
                        while os.path.exists(file_path):
                            name, ext = os.path.splitext(original_path)
                            file_path = f"{name}_{counter}{ext}"
                            counter += 1

                        with open(file_path, 'wb') as f:
                            f.write(attachment.Contents)

                        extraction_log.append({
                            'source_email': eml_file,
                            'attachment_name': attachment.Name,
                            'output_path': file_path,
                            'size': len(attachment.Contents)
                        })

            except Exception as e:
                print(f"Error processing {eml_file}: {e}")

        return all_attachments, extraction_log

    def filter_by_type(self, collection, file_extensions):
        """Filter attachments by file extensions."""

        filtered = MailAttachmentCollection()

        for attachment in collection.export_as_list():
            if attachment.Name:
                _, ext = os.path.splitext(attachment.Name.lower())
                if ext in [e.lower() for e in file_extensions]:
                    filtered.append(attachment)

        return filtered

    def filter_by_size(self, collection, min_size=0, max_size=float('inf')):
        """Filter attachments by size range."""

        filtered = MailAttachmentCollection()

        for attachment in collection.export_as_list():
            size = len(attachment.Contents)
            if min_size <= size <= max_size:
                filtered.append(attachment)

        return filtered

    def generate_summary_report(self, collection):
        """Generate summary report for attachment collection."""

        if collection.length() == 0:
            return "No attachments found."

        total_size = 0
        file_types = {}
        size_distribution = {'small': 0, 'medium': 0, 'large': 0}

        for attachment in collection.export_as_list():
            size = len(attachment.Contents)
            total_size += size

            # File type analysis
            if attachment.Name:
                _, ext = os.path.splitext(attachment.Name.lower())
                file_types[ext] = file_types.get(ext, 0) + 1

            # Size distribution
            if size < 1024 * 1024:  # < 1MB
                size_distribution['small'] += 1
            elif size < 10 * 1024 * 1024:  # < 10MB
                size_distribution['medium'] += 1
            else:
                size_distribution['large'] += 1

        report = f"""
Attachment Collection Summary
============================
Total attachments: {collection.length()}
Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)

File types:
{chr(10).join(f"  {ext or 'no extension'}: {count}" for ext, count in sorted(file_types.items()))}

Size distribution:
  Small (< 1MB): {size_distribution['small']}
  Medium (1-10MB): {size_distribution['medium']}
  Large (> 10MB): {size_distribution['large']}
        """

        return report.strip()

# Usage example
def demo_batch_processing():
    processor = AttachmentBatchProcessor("/path/to/output")

    # Process multiple EML files
    eml_files = [
        "/path/to/email1.eml",
        "/path/to/email2.eml",
        "/path/to/email3.eml"
    ]

    all_attachments, log = processor.extract_all_attachments(eml_files)

    print(f"Extracted {all_attachments.length()} total attachments")

    # Filter by type
    image_attachments = processor.filter_by_type(
        all_attachments,
        ['.jpg', '.png', '.gif']
    )
    print(f"Found {image_attachments.length()} image attachments")

    # Filter by size
    large_attachments = processor.filter_by_size(
        all_attachments,
        min_size=1024*1024  # > 1MB
    )
    print(f"Found {large_attachments.length()} large attachments")

    # Generate report
    report = processor.generate_summary_report(all_attachments)
    print(report)

demo_batch_processing()
```

### Attachment Deduplication

```python
import hashlib
from EMLMailReader import MailAttachmentCollection

def deduplicate_attachments(collection):
    """Remove duplicate attachments based on content hash."""

    unique_attachments = MailAttachmentCollection()
    seen_hashes = set()
    duplicates = []

    for attachment in collection.export_as_list():
        # Calculate content hash
        content_hash = hashlib.md5(attachment.Contents).hexdigest()

        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_attachments.append(attachment)
        else:
            duplicates.append({
                'name': attachment.Name,
                'size': len(attachment.Contents),
                'hash': content_hash
            })

    return unique_attachments, duplicates

def find_similar_attachments(collection):
    """Find attachments with same name but different content."""

    by_name = {}

    # Group by filename
    for attachment in collection.export_as_list():
        name = attachment.Name or "unnamed"
        if name not in by_name:
            by_name[name] = []
        by_name[name].append(attachment)

    # Find files with same name but different content
    similar = {}

    for name, attachments in by_name.items():
        if len(attachments) > 1:
            # Check if contents are different
            hashes = set()
            for att in attachments:
                content_hash = hashlib.md5(att.Contents).hexdigest()
                hashes.add(content_hash)

            if len(hashes) > 1:  # Different content
                similar[name] = {
                    'count': len(attachments),
                    'sizes': [len(att.Contents) for att in attachments],
                    'variations': len(hashes)
                }

    return similar

# Usage
def demo_deduplication():
    # Assume we have a collection with some duplicates
    collection = MailAttachmentCollection()

    # Add some test attachments (duplicates would be added in real scenario)
    # ... add attachments to collection ...

    unique, duplicates = deduplicate_attachments(collection)

    print(f"Original: {collection.length()} attachments")
    print(f"Unique: {unique.length()} attachments")
    print(f"Duplicates removed: {len(duplicates)}")

    if duplicates:
        print("\\nDuplicate files:")
        for dup in duplicates:
            print(f"  {dup['name']} ({dup['size']} bytes)")

    similar = find_similar_attachments(collection)
    if similar:
        print("\\nFiles with same name but different content:")
        for name, info in similar.items():
            print(f"  {name}: {info['count']} versions, {info['variations']} unique")

demo_deduplication()
```

### Attachment Archive Creation

```python
import zipfile
import tempfile
import os
from EMLMailReader import MailAttachmentCollection

class AttachmentArchiver:
    """Create archives from attachment collections."""

    def create_zip_archive(self, collection, archive_path, include_metadata=True):
        """Create a ZIP archive containing all attachments."""

        if collection.length() == 0:
            raise ValueError("No attachments to archive")

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            attachment_index = []

            for i, attachment in enumerate(collection.export_as_list()):
                # Generate unique filename for archive
                filename = attachment.Name or f"attachment_{i+1}"

                # Handle duplicate names within archive
                counter = 1
                original_filename = filename
                existing_names = zipf.namelist()

                while filename in existing_names:
                    name, ext = os.path.splitext(original_filename)
                    filename = f"{name}_{counter}{ext}"
                    counter += 1

                # Add file to archive
                zipf.writestr(filename, attachment.Contents)

                # Collect metadata
                if include_metadata:
                    metadata = {
                        'original_name': attachment.Name,
                        'archive_name': filename,
                        'size': len(attachment.Contents),
                        'content_type': attachment.ContentType.MediaType if attachment.ContentType else None,
                        'content_id': attachment.ContentID or None
                    }
                    attachment_index.append(metadata)

            # Add metadata file if requested
            if include_metadata:
                import json
                metadata_json = json.dumps(attachment_index, indent=2)
                zipf.writestr('_attachment_metadata.json', metadata_json)

        return archive_path

    def create_categorized_archive(self, collection, archive_path):
        """Create archive with attachments organized in folders by type."""

        file_categories = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'documents': ['.pdf', '.doc', '.docx', '.txt'],
            'spreadsheets': ['.xls', '.xlsx', '.csv'],
            'archives': ['.zip', '.rar', '.7z'],
            'other': []
        }

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for attachment in collection.export_as_list():
                # Determine category
                category = 'other'
                if attachment.Name:
                    _, ext = os.path.splitext(attachment.Name.lower())
                    for cat, extensions in file_categories.items():
                        if ext in extensions:
                            category = cat
                            break

                # Create path within archive
                filename = attachment.Name or 'unnamed'
                archive_path_internal = f"{category}/{filename}"

                # Handle duplicates
                counter = 1
                original_path = archive_path_internal
                while archive_path_internal in zipf.namelist():
                    name, ext = os.path.splitext(original_path)
                    archive_path_internal = f"{category}/{os.path.basename(name)}_{counter}{ext}"
                    counter += 1

                zipf.writestr(archive_path_internal, attachment.Contents)

        return archive_path

# Usage
def demo_archiving():
    # Assume we have a collection with attachments
    collection = MailAttachmentCollection()
    # ... populate collection ...

    archiver = AttachmentArchiver()

    # Create simple archive
    archive_path = "/path/to/attachments.zip"
    archiver.create_zip_archive(collection, archive_path)
    print(f"Created archive: {archive_path}")

    # Create categorized archive
    categorized_path = "/path/to/attachments_categorized.zip"
    archiver.create_categorized_archive(collection, categorized_path)
    print(f"Created categorized archive: {categorized_path}")

demo_archiving()
```

### Collection Statistics and Analysis

```python
from EMLMailReader import MailAttachmentCollection
import mimetypes
from collections import defaultdict

class AttachmentAnalyzer:
    """Analyze attachment collections for insights and statistics."""

    def analyze_collection(self, collection):
        """Perform comprehensive analysis of attachment collection."""

        if collection.length() == 0:
            return {'empty': True}

        analysis = {
            'total_count': collection.length(),
            'total_size': 0,
            'file_types': defaultdict(int),
            'size_distribution': {'tiny': 0, 'small': 0, 'medium': 0, 'large': 0, 'huge': 0},
            'name_analysis': {'named': 0, 'unnamed': 0},
            'embedded_content': 0,
            'largest_file': {'name': '', 'size': 0},
            'smallest_file': {'name': '', 'size': float('inf')},
            'duplicate_names': defaultdict(int)
        }

        for attachment in collection.export_as_list():
            size = len(attachment.Contents)
            analysis['total_size'] += size

            # File type analysis
            if attachment.Name:
                _, ext = os.path.splitext(attachment.Name.lower())
                analysis['file_types'][ext or 'no_extension'] += 1
                analysis['name_analysis']['named'] += 1
                analysis['duplicate_names'][attachment.Name] += 1
            else:
                analysis['name_analysis']['unnamed'] += 1

            # Size distribution
            if size < 1024:  # < 1KB
                analysis['size_distribution']['tiny'] += 1
            elif size < 1024 * 1024:  # < 1MB
                analysis['size_distribution']['small'] += 1
            elif size < 10 * 1024 * 1024:  # < 10MB
                analysis['size_distribution']['medium'] += 1
            elif size < 100 * 1024 * 1024:  # < 100MB
                analysis['size_distribution']['large'] += 1
            else:
                analysis['size_distribution']['huge'] += 1

            # Largest/smallest tracking
            if size > analysis['largest_file']['size']:
                analysis['largest_file'] = {'name': attachment.Name or 'unnamed', 'size': size}

            if size < analysis['smallest_file']['size']:
                analysis['smallest_file'] = {'name': attachment.Name or 'unnamed', 'size': size}

            # Embedded content
            if attachment.ContentID:
                analysis['embedded_content'] += 1

        # Find actual duplicates (same name, more than 1)
        analysis['actual_duplicates'] = {
            name: count for name, count in analysis['duplicate_names'].items()
            if count > 1
        }

        return analysis

    def generate_detailed_report(self, collection):
        """Generate a detailed text report."""

        analysis = self.analyze_collection(collection)

        if analysis.get('empty'):
            return "No attachments found in collection."

        report = f"""
Attachment Collection Analysis Report
===================================

Overview:
  Total attachments: {analysis['total_count']}
  Total size: {analysis['total_size']:,} bytes ({analysis['total_size']/1024/1024:.2f} MB)
  Average size: {analysis['total_size']//analysis['total_count']:,} bytes

File Types:
{chr(10).join(f"  {ext}: {count}" for ext, count in sorted(analysis['file_types'].items(), key=lambda x: x[1], reverse=True))}

Size Distribution:
  Tiny (< 1KB): {analysis['size_distribution']['tiny']}
  Small (1KB - 1MB): {analysis['size_distribution']['small']}
  Medium (1MB - 10MB): {analysis['size_distribution']['medium']}
  Large (10MB - 100MB): {analysis['size_distribution']['large']}
  Huge (> 100MB): {analysis['size_distribution']['huge']}

File Naming:
  Named files: {analysis['name_analysis']['named']}
  Unnamed files: {analysis['name_analysis']['unnamed']}

Special Content:
  Embedded content (with Content-ID): {analysis['embedded_content']}

Extremes:
  Largest file: {analysis['largest_file']['name']} ({analysis['largest_file']['size']:,} bytes)
  Smallest file: {analysis['smallest_file']['name']} ({analysis['smallest_file']['size']:,} bytes)
        """

        if analysis['actual_duplicates']:
            report += "\nDuplicate Filenames:\n"
            for name, count in analysis['actual_duplicates'].items():
                report += f"  {name}: {count} files\n"

        return report.strip()

# Usage
def demo_analysis():
    # Assume we have a collection
    collection = MailAttachmentCollection()
    # ... populate collection ...

    analyzer = AttachmentAnalyzer()

    # Get analysis data
    analysis = analyzer.analyze_collection(collection)
    print(f"Analysis complete: {analysis['total_count']} attachments analyzed")

    # Generate detailed report
    report = analyzer.generate_detailed_report(collection)
    print(report)

    # Save report to file
    with open('/path/to/attachment_analysis.txt', 'w') as f:
        f.write(report)

demo_analysis()
```

## Best Practices

### 1. Check Collection Size Before Processing

```python
if collection.length() > 0:
    # Process attachments
    for attachment in collection.export_as_list():
        # Handle each attachment
        pass
else:
    print("No attachments to process")
```

### 2. Use export_as_list() for Safe Iteration

```python
# Recommended approach
attachment_list = collection.export_as_list()
for attachment in attachment_list:
    # Safe to modify attachment without affecting collection
    process_attachment(attachment)
```

### 3. Handle Memory Usage with Large Collections

```python
def process_large_collection(collection, batch_size=10):
    """Process large collections in batches to manage memory."""

    attachment_list = collection.export_as_list()

    for i in range(0, len(attachment_list), batch_size):
        batch = attachment_list[i:i + batch_size]

        for attachment in batch:
            # Process individual attachment
            process_attachment(attachment)

        # Optional: Force garbage collection between batches
        import gc
        gc.collect()
```

### 4. Validate Collection Contents

```python
def validate_collection(collection):
    """Validate all attachments in collection."""

    issues = []

    for i, attachment in enumerate(collection.export_as_list()):
        if not attachment.Contents:
            issues.append(f"Attachment {i+1}: No content")

        if not attachment.Name:
            issues.append(f"Attachment {i+1}: No filename")

        if len(attachment.Contents) == 0:
            issues.append(f"Attachment {i+1} ({attachment.Name}): Empty file")

    return issues
```

## Related Classes

- [MailAttachment](MailAttachment.md) - Individual email attachment representation
- [RxMailMessage](RxMailMessage.md) - Email message containing attachment collections
- [MailReader](MailReader.md) - Parser that creates MailAttachmentCollection instances
