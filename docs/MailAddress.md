# MailAddress

## Overview

The `MailAddress` class represents an individual email address with optional display name. It handles parsing of email addresses in various formats commonly found in email headers, supporting both simple addresses and addresses with display names.

## Class Definition

```python
class MailAddress:
    """
    A class to represent an email address with optional display name.

    This class parses and stores email addresses in the format used by email headers,
    supporting both simple addresses (user@domain.com) and addresses with display names
    ("John Doe" <user@domain.com>).
    """
```

## Constructor

### `__init__(self)`

Initializes a new MailAddress instance with empty display name and email address.

**Example:**
```python
from EMLMailReader import MailAddress

# Create a new mail address instance
address = MailAddress()
```

## Properties

### `DisplayName` (str)
**Type:** `str`
**Description:** The human-readable name associated with the email address (optional).

```python
# Access display name
print(f"Display Name: {address.DisplayName}")

# Set display name manually
address.DisplayName = "John Doe"
```

### `Email` (str)
**Type:** `str`
**Description:** The actual email address (user@domain.com format).

```python
# Access email address
print(f"Email: {address.Email}")

# Set email manually
address.Email = "john.doe@example.com"
```

## Public Methods

### `parse(self, MailAddressString: str)`

Parses an email address string and extracts the display name and email components.

**Parameters:**
- `MailAddressString` (str): Email address string to parse

**Returns:**
- `None` - modifies the object's properties in place

**Supported Formats:**
- Simple email: `user@domain.com`
- With display name: `"John Doe" <user@domain.com>`
- With display name (no quotes): `John Doe <user@domain.com>`

**Example:**
```python
from EMLMailReader import MailAddress

# Parse simple email address
address1 = MailAddress()
address1.parse("user@example.com")
print(f"Email: {address1.Email}")  # user@example.com
print(f"Display Name: {address1.DisplayName}")  # (empty)

# Parse email with display name
address2 = MailAddress()
address2.parse('"John Doe" <john.doe@example.com>')
print(f"Email: {address2.Email}")  # john.doe@example.com
print(f"Display Name: {address2.DisplayName}")  # John Doe

# Parse email with unquoted display name
address3 = MailAddress()
address3.parse('Jane Smith <jane.smith@example.com>')
print(f"Email: {address3.Email}")  # jane.smith@example.com
print(f"Display Name: {address3.DisplayName}")  # Jane Smith
```

### `__str__(self) -> str`

Returns a properly formatted email address string.

**Returns:**
- `str`: Formatted email address string

**Format:**
- If display name exists: `"Display Name" <email@domain.com>`
- If no display name: `email@domain.com`

**Example:**
```python
# With display name
address = MailAddress()
address.DisplayName = "John Doe"
address.Email = "john.doe@example.com"
print(str(address))  # John Doe <john.doe@example.com>

# Without display name
address2 = MailAddress()
address2.Email = "user@example.com"
print(str(address2))  # user@example.com
```

## Usage Examples

### Basic Address Parsing

```python
from EMLMailReader import MailAddress

def parse_email_addresses():
    """Demonstrate basic email address parsing."""

    # Test various email formats
    test_addresses = [
        "simple@example.com",
        "John Doe <john.doe@example.com>",
        '"Jane Smith" <jane.smith@example.com>',
        "support@company.org",
        '"Customer Service" <support@company.org>'
    ]

    for addr_string in test_addresses:
        address = MailAddress()
        address.parse(addr_string)

        print(f"Original: {addr_string}")
        print(f"  Email: {address.Email}")
        print(f"  Display Name: '{address.DisplayName}'")
        print(f"  Formatted: {str(address)}")
        print()

# Usage
parse_email_addresses()
```

### Email Validation and Processing

```python
import re
from EMLMailReader import MailAddress

def validate_email_address(email_string):
    """Validate and parse an email address."""

    address = MailAddress()

    try:
        address.parse(email_string)

        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, address.Email):
            return None, f"Invalid email format: {address.Email}"

        return address, None

    except Exception as e:
        return None, f"Parsing error: {e}"

def process_email_list(email_strings):
    """Process a list of email address strings."""

    valid_addresses = []
    invalid_addresses = []

    for email_string in email_strings:
        address, error = validate_email_address(email_string)

        if address:
            valid_addresses.append(address)
            print(f"✓ Valid: {address}")
        else:
            invalid_addresses.append((email_string, error))
            print(f"✗ Invalid: {email_string} - {error}")

    return valid_addresses, invalid_addresses

# Usage
email_list = [
    "user@example.com",
    "John Doe <john@example.com>",
    "invalid-email",
    '"Jane Smith" <jane@company.org>',
    "malformed <incomplete"
]

valid, invalid = process_email_list(email_list)
print(f"\\nSummary: {len(valid)} valid, {len(invalid)} invalid addresses")
```

### Address Book Management

```python
from EMLMailReader import MailAddress

class AddressBook:
    """Simple address book using MailAddress objects."""

    def __init__(self):
        self.contacts = {}

    def add_contact(self, name, email_string):
        """Add a contact to the address book."""
        address = MailAddress()
        address.parse(email_string)

        # Use display name from address if no name provided
        if not name and address.DisplayName:
            name = address.DisplayName
        elif name and not address.DisplayName:
            address.DisplayName = name

        self.contacts[name] = address

    def get_contact(self, name):
        """Get a contact by name."""
        return self.contacts.get(name)

    def find_by_email(self, email):
        """Find contact by email address."""
        for name, address in self.contacts.items():
            if address.Email.lower() == email.lower():
                return name, address
        return None, None

    def list_contacts(self):
        """List all contacts."""
        for name, address in self.contacts.items():
            print(f"{name}: {address}")

    def export_for_email_client(self):
        """Export addresses in email client format."""
        addresses = []
        for address in self.contacts.values():
            addresses.append(str(address))
        return "; ".join(addresses)

# Usage
book = AddressBook()

# Add contacts
book.add_contact("John", "john@example.com")
book.add_contact("", '"Jane Doe" <jane@company.org>')  # Name from display name
book.add_contact("Support Team", "support@company.org")

# List contacts
print("Address Book:")
book.list_contacts()

# Find contact
name, address = book.find_by_email("john@example.com")
if address:
    print(f"\\nFound: {name} - {address}")

# Export for email client
print(f"\\nEmail client format: {book.export_for_email_client()}")
```

### Encoded Header Handling

```python
from EMLMailReader import MailAddress, TextEncoding

def parse_encoded_address(encoded_string):
    """Parse email address with encoded display name."""

    address = MailAddress()
    address.parse(encoded_string)

    print(f"Original: {encoded_string}")
    print(f"Parsed Email: {address.Email}")
    print(f"Parsed Display Name: {address.DisplayName}")
    print(f"Formatted: {str(address)}")

    return address

# Test with encoded display names (common in international emails)
test_cases = [
    '=?UTF-8?B?Sm9obiBEb2U=?= <john@example.com>',  # Base64 encoded "John Doe"
    '=?UTF-8?Q?Jane_Smith?= <jane@example.com>',      # Quoted-printable encoded
    'normal@example.com',                             # No encoding
    '"Regular Name" <regular@example.com>'            # Regular quoted name
]

print("Testing encoded address parsing:")
for test_case in test_cases:
    parse_encoded_address(test_case)
    print()
```

### Integration with Email Parsing

```python
from EMLMailReader import MailReader, MailAddress

def extract_all_addresses(eml_file):
    """Extract all email addresses from an EML file."""

    reader = MailReader()
    message = reader.get_email(eml_file)

    if not message:
        print("Failed to parse email")
        return

    all_addresses = {}

    # From address
    if message.From:
        all_addresses['From'] = [message.From]

    # To addresses
    if message.To.length() > 0:
        all_addresses['To'] = message.To.export_as_list()

    # Cc addresses
    if message.Cc.length() > 0:
        all_addresses['Cc'] = message.Cc.export_as_list()

    # Bcc addresses
    if message.Bcc.length() > 0:
        all_addresses['Bcc'] = message.Bcc.export_as_list()

    # Reply-To addresses
    if message.ReplyTo.length() > 0:
        all_addresses['Reply-To'] = message.ReplyTo.export_as_list()

    # Display results
    for header_type, addresses in all_addresses.items():
        print(f"{header_type}:")
        for address in addresses:
            print(f"  {address.Email}")
            if address.DisplayName:
                print(f"    Display Name: {address.DisplayName}")
        print()

    return all_addresses

# Usage
addresses = extract_all_addresses("/path/to/email.eml")
```

### Custom Address Formatting

```python
from EMLMailReader import MailAddress

class FormattedMailAddress(MailAddress):
    """Extended MailAddress with custom formatting options."""

    def format_for_display(self):
        """Format for user-friendly display."""
        if self.DisplayName:
            return f"{self.DisplayName} ({self.Email})"
        return self.Email

    def format_for_csv(self):
        """Format for CSV export."""
        display = self.DisplayName.replace('"', '""') if self.DisplayName else ""
        return f'"{display}","{self.Email}"'

    def format_short(self, max_length=30):
        """Format with length limit."""
        full_format = str(self)
        if len(full_format) <= max_length:
            return full_format

        if self.DisplayName:
            # Try just first name
            first_name = self.DisplayName.split()[0]
            short_format = f"{first_name} <{self.Email}>"
            if len(short_format) <= max_length:
                return short_format

        # Fall back to just email
        return self.Email

    def get_domain(self):
        """Extract domain from email address."""
        if '@' in self.Email:
            return self.Email.split('@')[1]
        return ""

# Usage
def demo_custom_formatting():
    address = FormattedMailAddress()
    address.parse('"John David Smith" <john.smith@verylongdomainname.com>')

    print(f"Original: {address}")
    print(f"Display: {address.format_for_display()}")
    print(f"CSV: {address.format_for_csv()}")
    print(f"Short: {address.format_short(25)}")
    print(f"Domain: {address.get_domain()}")

demo_custom_formatting()
```

## Best Practices

### 1. Always Validate Email Addresses

```python
import re

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Use with MailAddress
address = MailAddress()
address.parse(email_string)

if is_valid_email(address.Email):
    # Process valid email
    pass
else:
    # Handle invalid email
    pass
```

### 2. Handle Encoding Properly

```python
# The MailAddress class automatically handles encoded display names
# through the TextEncoding.decode_header() method during parsing
address = MailAddress()
address.parse('=?UTF-8?B?Sm9obiBEb2U=?= <john@example.com>')
# Display name is automatically decoded
```

### 3. Safe String Representation

```python
def safe_address_string(address):
    """Safely convert address to string, handling None values."""
    if not address:
        return "Unknown"

    try:
        return str(address)
    except:
        return address.Email if address.Email else "Unknown"
```

### 4. Compare Addresses Properly

```python
def addresses_equal(addr1, addr2):
    """Compare two MailAddress objects for equality."""
    if not addr1 or not addr2:
        return False

    return addr1.Email.lower() == addr2.Email.lower()

def find_duplicate_addresses(address_list):
    """Find duplicate email addresses in a list."""
    seen_emails = set()
    duplicates = []

    for address in address_list:
        email_lower = address.Email.lower()
        if email_lower in seen_emails:
            duplicates.append(address)
        else:
            seen_emails.add(email_lower)

    return duplicates
```

## Related Classes

- [MailAddressCollection](MailAddressCollection.md) - Collection of MailAddress instances
- [TextEncoding](TextEncoding.md) - Text encoding and decoding utilities
- [RxMailMessage](RxMailMessage.md) - Email message representation using MailAddress
