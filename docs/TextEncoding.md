# TextEncoding

## Overview

The `TextEncoding` class is a static utility class that provides methods for decoding various text encodings used in MIME content. It handles Base64 and Quoted-Printable encoded content commonly found in email messages, with proper character set handling for internationalization.

## Class Definition

```python
class TextEncoding:
    """
    Static utility class for decoding various text encodings used in MIME content.

    This class provides methods to decode Base64 and Quoted-Printable encoded content
    commonly found in email messages. It handles both text content and binary file
    attachments, with proper character set handling for internationalization.
    """
```

## Static Methods

### `decode_quoted_printable_string(encoded_string: str, string_charset: str, is_header: bool) -> str`

**[INTERNAL USE ONLY]** Decodes Quoted-Printable encoded text content to readable string.

**Parameters:**
- `encoded_string` (str): Quoted-Printable encoded string to decode
- `string_charset` (str): Character encoding of the original text
- `is_header` (bool): Whether the content is from an email header

**Returns:**
- `str`: Decoded Unicode string with proper character encoding

### `decode_base64_string(encoded_string: str, string_charset: str = "utf-8") -> str`

**[INTERNAL USE ONLY]** Decodes Base64 encoded text content to readable string.

**Parameters:**
- `encoded_string` (str): Base64 encoded string to decode
- `string_charset` (str): Character encoding for the decoded text (defaults to UTF-8)

**Returns:**
- `str`: Decoded Unicode string with proper character encoding

### `decode_base64_file(file_contents: str) -> bytes`

Decodes Base64 encoded binary file content back to original bytes.

**Parameters:**
- `file_contents` (str): Base64 encoded string representing binary file data

**Returns:**
- `bytes`: Original binary file content as bytes object

**Example:**
```python
from EMLMailReader import TextEncoding

# Decode a Base64 encoded file
base64_content = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
decoded_bytes = TextEncoding.decode_base64_file(base64_content)

# Save to file
with open("decoded_image.png", "wb") as f:
    f.write(decoded_bytes)
```

### `decode_header(encoded_string: str) -> str`

Decodes RFC 2047 encoded email headers to readable Unicode text.

**Parameters:**
- `encoded_string` (str): Potentially encoded header string to decode

**Returns:**
- `str`: Decoded Unicode string, or original string if no encoding detected

**Raises:**
- `InvalidEncodingError`: If an unsupported encoding method is encountered

**Example:**
```python
from EMLMailReader import TextEncoding

# Decode various header formats
headers = [
    "=?UTF-8?B?Sm9obiBEb2U=?=",  # Base64 encoded "John Doe"
    "=?UTF-8?Q?Jane_Smith?=",      # Quoted-printable encoded "Jane Smith"
    "Regular Header Text",          # No encoding
    "=?ISO-8859-1?Q?Caf=E9?="      # "Café" in ISO-8859-1
]

for header in headers:
    decoded = TextEncoding.decode_header(header)
    print(f"Original: {header}")
    print(f"Decoded:  {decoded}")
    print()
```

## Usage Examples

### Working with Encoded Headers

```python
from EMLMailReader import TextEncoding, InvalidEncodingError

def decode_email_headers(headers_dict):
    """Decode all potentially encoded headers in an email."""

    decoded_headers = {}

    for header_name, header_value in headers_dict.items():
        try:
            # Headers that commonly contain encoded content
            if header_name.lower() in ['subject', 'from', 'to', 'cc', 'reply-to']:
                decoded_value = TextEncoding.decode_header(header_value)
                decoded_headers[header_name] = decoded_value

                if decoded_value != header_value:
                    print(f"Decoded {header_name}: {header_value} -> {decoded_value}")
            else:
                decoded_headers[header_name] = header_value

        except InvalidEncodingError as e:
            print(f"Could not decode header {header_name}: {e}")
            decoded_headers[header_name] = header_value  # Keep original

    return decoded_headers

# Example usage
headers = {
    'Subject': '=?UTF-8?B?UmU6IEltcG9ydGFudCBNZWV0aW5n?=',
    'From': '=?UTF-8?Q?John_Doe?= <john@example.com>',
    'Date': 'Wed, 21 Feb 2024 09:55:06 -0600',
    'Message-ID': '<123456@example.com>'
}

decoded = decode_email_headers(headers)
```

### File Attachment Processing

```python
from EMLMailReader import TextEncoding
import base64
import os

def extract_base64_attachment(base64_content, output_path, chunk_size=1024*1024):
    """Extract large Base64 encoded attachments efficiently."""

    try:
        # For very large files, process in chunks to manage memory
        if len(base64_content) > chunk_size:
            print(f"Processing large attachment ({len(base64_content)} chars)")

            # Remove any whitespace/newlines that might be in the Base64 data
            clean_content = ''.join(base64_content.split())

            # Decode in one go (the library handles this efficiently)
            decoded_bytes = TextEncoding.decode_base64_file(clean_content)
        else:
            decoded_bytes = TextEncoding.decode_base64_file(base64_content)

        # Write to file
        with open(output_path, 'wb') as f:
            f.write(decoded_bytes)

        print(f"Extracted attachment: {output_path} ({len(decoded_bytes)} bytes)")
        return True

    except Exception as e:
        print(f"Error extracting attachment: {e}")
        return False

# Example with a small Base64 encoded PDF
pdf_base64 = "JVBERi0xLjQKJdPr6eEKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPD4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmCjAwMDAwMDAwMDkgMDAwMDAgbgowMDAwMDAwMDc0IDAwMDAwIG4KMDAwMDAwMDEyMCAwMDAwMCBuCnRyYWlsZXIKPDwKL1NpemUgNAovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKMTc4CiUlRU9GCg=="

extract_base64_attachment(pdf_base64, "decoded_document.pdf")
```

### Custom Encoding Detection

```python
from EMLMailReader import TextEncoding
import re

class EnhancedTextDecoder:
    """Extended text decoding with additional features."""

    @staticmethod
    def detect_encoding_type(encoded_string):
        """Detect the type of encoding used in a string."""

        # Check for RFC 2047 encoded headers
        rfc2047_pattern = r'=\?([^?]+)\?([BbQq])\?([^?]+)\?='
        match = re.match(rfc2047_pattern, encoded_string)

        if match:
            charset, encoding, data = match.groups()
            return {
                'type': 'rfc2047',
                'charset': charset,
                'encoding': encoding.upper(),
                'data': data
            }

        # Check for Base64 (basic heuristic)
        if re.match(r'^[A-Za-z0-9+/]+={0,2}$', encoded_string.replace('\\n', '')):
            return {'type': 'base64', 'charset': 'unknown'}

        # Check for Quoted-Printable
        if '=' in encoded_string and re.search(r'=[0-9A-Fa-f]{2}', encoded_string):
            return {'type': 'quoted_printable', 'charset': 'unknown'}

        return {'type': 'plain', 'charset': 'unknown'}

    @staticmethod
    def decode_with_fallback(encoded_string, fallback_charset='utf-8'):
        """Decode string with fallback options."""

        try:
            # Try standard decoding first
            return TextEncoding.decode_header(encoded_string)
        except:
            # Try direct Base64 decode as fallback
            try:
                import base64
                decoded_bytes = base64.b64decode(encoded_string)
                return decoded_bytes.decode(fallback_charset, errors='replace')
            except:
                # Return original if all fails
                return encoded_string

    @staticmethod
    def batch_decode_headers(header_dict):
        """Decode multiple headers with detailed reporting."""

        results = {}

        for name, value in header_dict.items():
            encoding_info = EnhancedTextDecoder.detect_encoding_type(value)

            if encoding_info['type'] != 'plain':
                try:
                    decoded = TextEncoding.decode_header(value)
                    results[name] = {
                        'original': value,
                        'decoded': decoded,
                        'encoding_info': encoding_info,
                        'success': True
                    }
                except Exception as e:
                    results[name] = {
                        'original': value,
                        'decoded': value,  # Keep original
                        'encoding_info': encoding_info,
                        'success': False,
                        'error': str(e)
                    }
            else:
                results[name] = {
                    'original': value,
                    'decoded': value,
                    'encoding_info': encoding_info,
                    'success': True
                }

        return results

# Usage example
def demo_enhanced_decoding():
    decoder = EnhancedTextDecoder()

    test_headers = {
        'Subject': '=?UTF-8?B?VGVzdCBTdWJqZWN0?=',
        'From': '=?ISO-8859-1?Q?Caf=E9?= <cafe@example.com>',
        'Plain': 'Regular header text',
        'Invalid': '=?INVALID?X?BadEncoding?='
    }

    results = decoder.batch_decode_headers(test_headers)

    for name, result in results.items():
        print(f"{name}:")
        print(f"  Original: {result['original']}")
        print(f"  Decoded: {result['decoded']}")
        print(f"  Encoding: {result['encoding_info']['type']}")
        print(f"  Success: {result['success']}")
        if not result['success']:
            print(f"  Error: {result['error']}")
        print()

demo_enhanced_decoding()
```

## Best Practices

### 1. Always Handle Encoding Errors

```python
from EMLMailReader import TextEncoding, InvalidEncodingError

def safe_header_decode(header_value):
    """Safely decode header with error handling."""
    try:
        return TextEncoding.decode_header(header_value)
    except InvalidEncodingError:
        # Return original value if decoding fails
        return header_value
    except Exception:
        # Handle any other unexpected errors
        return header_value
```

### 2. Validate Base64 Content Before Decoding

```python
import re

def is_valid_base64(content):
    """Check if content appears to be valid Base64."""
    # Remove whitespace
    clean_content = ''.join(content.split())

    # Check length (must be multiple of 4)
    if len(clean_content) % 4 != 0:
        return False

    # Check character set
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', clean_content):
        return False

    return True

def safe_base64_decode(base64_content):
    """Safely decode Base64 content."""
    if not is_valid_base64(base64_content):
        raise ValueError("Invalid Base64 content")

    return TextEncoding.decode_base64_file(base64_content)
```

### 3. Handle Large Attachments Efficiently

```python
def decode_large_attachment(base64_content, max_memory_mb=100):
    """Decode large attachments with memory management."""

    # Estimate decoded size (Base64 is ~133% of original)
    estimated_size = len(base64_content) * 0.75
    max_size = max_memory_mb * 1024 * 1024

    if estimated_size > max_size:
        print(f"Warning: Large attachment detected ({estimated_size/1024/1024:.1f} MB)")
        print("Consider processing in chunks or increasing memory limit")

        # Could implement streaming decode here for very large files
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            return None

    return TextEncoding.decode_base64_file(base64_content)
```

## Related Classes

- [MailAddress](MailAddress.md) - Uses TextEncoding for display name decoding
- [RxMailMessage](RxMailMessage.md) - Uses TextEncoding for header and body decoding
- [MailReader](MailReader.md) - Uses TextEncoding extensively during parsing
- [Exceptions](Exceptions.md) - InvalidEncodingError may be raised
