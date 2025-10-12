# MailAddressCollection

## Overview

The `MailAddressCollection` class is a container for managing multiple `MailAddress` instances. It provides functionality for storing, accessing, and manipulating collections of email addresses commonly found in email headers like To, Cc, Bcc, and Reply-To fields.

## Class Definition

```python
class MailAddressCollection:
    """
    A collection class to manage multiple MailAddress instances.

    This class provides a container for storing and manipulating lists of email addresses
    commonly found in email headers like To, Cc, Bcc, and Reply-To fields.
    """
```

## Constructor

### `__init__(self)`

Initializes a new empty MailAddressCollection instance.

**Example:**
```python
from EMLMailReader import MailAddressCollection

# Create a new collection
addresses = MailAddressCollection()
```

## Properties

### `__addresses` (list[MailAddress])
**Type:** `list[MailAddress]` (private)
**Description:** Internal list containing MailAddress instances in the collection. This property is private and should not be accessed directly.

## Public Methods

### `append(self, address: MailAddress)`

Adds a MailAddress instance to the end of the collection.

**Parameters:**
- `address` (MailAddress): MailAddress object to be added to the collection

**Returns:**
- `None` - modifies the collection in place

**Example:**
```python
from EMLMailReader import MailAddress, MailAddressCollection

# Create collection and addresses
collection = MailAddressCollection()

# Create and add addresses
address1 = MailAddress()
address1.parse("john@example.com")

address2 = MailAddress()
address2.parse("Jane Doe <jane@example.com>")

# Add to collection
collection.append(address1)
collection.append(address2)

print(f"Collection has {collection.length()} addresses")
```

### `length(self) -> int`

Returns the number of MailAddress items in the collection.

**Returns:**
- `int`: Count of MailAddress instances in the collection

**Example:**
```python
collection = MailAddressCollection()
print(f"Empty collection length: {collection.length()}")  # 0

# Add some addresses
address = MailAddress()
address.parse("user@example.com")
collection.append(address)

print(f"Collection length after adding: {collection.length()}")  # 1
```

### `export_as_list(self) -> list`

Exports the collection as a new list of MailAddress instances.

**Returns:**
- `list`: A new list containing deep copies of all MailAddress instances

**Note:** This method creates deep copies to prevent external modification of the collection's internal state.

**Example:**
```python
# Export addresses as list for processing
address_list = collection.export_as_list()

for address in address_list:
    print(f"Email: {address.Email}")
    if address.DisplayName:
        print(f"Name: {address.DisplayName}")
```

### `__str__(self) -> str`

Returns a semicolon-separated string of all email addresses in the collection.

**Returns:**
- `str`: Semicolon-delimited string of formatted email addresses

**Format:** This format is commonly used in email headers for multiple recipients.

**Example:**
```python
collection = MailAddressCollection()

# Add multiple addresses
addr1 = MailAddress()
addr1.parse("john@example.com")
collection.append(addr1)

addr2 = MailAddress()
addr2.parse("Jane Doe <jane@example.com>")
collection.append(addr2)

print(str(collection))
# Output: john@example.com;Jane Doe <jane@example.com>
```

## Usage Examples

### Basic Collection Operations

```python
from EMLMailReader import MailAddress, MailAddressCollection

def create_recipient_list():
    """Create and manage a recipient list."""

    # Create collection
    recipients = MailAddressCollection()

    # Sample email addresses
    email_strings = [
        "john.doe@example.com",
        "Jane Smith <jane.smith@company.org>",
        '"Support Team" <support@helpdesk.com>',
        "admin@system.net"
    ]

    # Parse and add addresses
    for email_string in email_strings:
        address = MailAddress()
        address.parse(email_string)
        recipients.append(address)

    print(f"Created collection with {recipients.length()} recipients")
    print(f"Recipients: {recipients}")

    return recipients

# Usage
recipient_list = create_recipient_list()
```

### Working with Email Headers

```python
from EMLMailReader import MailReader, MailAddressCollection

def analyze_recipients(eml_file):
    """Analyze recipients in an email message."""

    reader = MailReader()
    message = reader.get_email(eml_file)

    if not message:
        print("Failed to parse email")
        return

    # Analyze different recipient types
    recipient_types = {
        'To': message.To,
        'Cc': message.Cc,
        'Bcc': message.Bcc,
        'Reply-To': message.ReplyTo
    }

    total_recipients = 0

    for header_type, collection in recipient_types.items():
        count = collection.length()
        total_recipients += count

        if count > 0:
            print(f"{header_type} ({count} recipients):")
            for address in collection.export_as_list():
                if address.DisplayName:
                    print(f"  {address.DisplayName} <{address.Email}>")
                else:
                    print(f"  {address.Email}")
        else:
            print(f"{header_type}: None")
        print()

    print(f"Total recipients: {total_recipients}")

    return recipient_types

# Usage
recipients = analyze_recipients("/path/to/email.eml")
```

### Collection Manipulation

```python
from EMLMailReader import MailAddress, MailAddressCollection

def merge_collections(*collections):
    """Merge multiple MailAddressCollections into one."""

    merged = MailAddressCollection()

    for collection in collections:
        for address in collection.export_as_list():
            merged.append(address)

    return merged

def remove_duplicates(collection):
    """Remove duplicate email addresses from collection."""

    seen_emails = set()
    unique_collection = MailAddressCollection()

    for address in collection.export_as_list():
        email_lower = address.Email.lower()
        if email_lower not in seen_emails:
            seen_emails.add(email_lower)
            unique_collection.append(address)

    return unique_collection

def filter_by_domain(collection, domain):
    """Filter addresses by domain."""

    filtered = MailAddressCollection()

    for address in collection.export_as_list():
        if address.Email.lower().endswith(f"@{domain.lower()}"):
            filtered.append(address)

    return filtered

# Usage example
def demo_collection_operations():
    # Create test collections
    to_recipients = MailAddressCollection()
    cc_recipients = MailAddressCollection()

    # Add some addresses with duplicates
    test_addresses = [
        "john@example.com",
        "jane@company.org",
        "john@example.com",  # Duplicate
        "admin@example.com",
        "support@company.org"
    ]

    for i, addr_str in enumerate(test_addresses):
        address = MailAddress()
        address.parse(addr_str)

        if i < 3:
            to_recipients.append(address)
        else:
            cc_recipients.append(address)

    print("Original collections:")
    print(f"To: {to_recipients}")
    print(f"Cc: {cc_recipients}")

    # Merge collections
    all_recipients = merge_collections(to_recipients, cc_recipients)
    print(f"\\nMerged: {all_recipients}")
    print(f"Merged count: {all_recipients.length()}")

    # Remove duplicates
    unique_recipients = remove_duplicates(all_recipients)
    print(f"\\nUnique: {unique_recipients}")
    print(f"Unique count: {unique_recipients.length()}")

    # Filter by domain
    example_domain = filter_by_domain(unique_recipients, "example.com")
    print(f"\\nExample.com domain: {example_domain}")
    print(f"Example.com count: {example_domain.length()}")

demo_collection_operations()
```

### Email List Management

```python
from EMLMailReader import MailAddress, MailAddressCollection
import csv
import json

class EmailListManager:
    """Advanced email list management using MailAddressCollection."""

    def __init__(self):
        self.lists = {}

    def create_list(self, list_name):
        """Create a new email list."""
        self.lists[list_name] = MailAddressCollection()

    def add_to_list(self, list_name, email_string):
        """Add an email address to a list."""
        if list_name not in self.lists:
            self.create_list(list_name)

        address = MailAddress()
        address.parse(email_string)
        self.lists[list_name].append(address)

    def get_list(self, list_name):
        """Get a specific email list."""
        return self.lists.get(list_name)

    def merge_lists(self, list1_name, list2_name, new_list_name):
        """Merge two lists into a new list."""
        if list1_name in self.lists and list2_name in self.lists:
            list1 = self.lists[list1_name]
            list2 = self.lists[list2_name]

            merged = MailAddressCollection()

            # Add all addresses from both lists
            for address in list1.export_as_list():
                merged.append(address)
            for address in list2.export_as_list():
                merged.append(address)

            self.lists[new_list_name] = merged

    def export_list_to_csv(self, list_name, filename):
        """Export email list to CSV file."""
        if list_name not in self.lists:
            return False

        collection = self.lists[list_name]

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Display Name', 'Email Address'])

            for address in collection.export_as_list():
                writer.writerow([address.DisplayName, address.Email])

        return True

    def import_list_from_csv(self, list_name, filename):
        """Import email list from CSV file."""
        self.create_list(list_name)
        collection = self.lists[list_name]

        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    address = MailAddress()
                    address.Email = row.get('Email Address', '')
                    address.DisplayName = row.get('Display Name', '')

                    if address.Email:  # Only add if email is present
                        collection.append(address)

            return True
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return False

    def get_statistics(self):
        """Get statistics about all lists."""
        stats = {}

        for list_name, collection in self.lists.items():
            addresses = collection.export_as_list()

            # Calculate statistics
            total_count = len(addresses)
            with_display_name = sum(1 for addr in addresses if addr.DisplayName)
            domains = {}

            for addr in addresses:
                if '@' in addr.Email:
                    domain = addr.Email.split('@')[1].lower()
                    domains[domain] = domains.get(domain, 0) + 1

            stats[list_name] = {
                'total_addresses': total_count,
                'with_display_name': with_display_name,
                'unique_domains': len(domains),
                'top_domains': sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]
            }

        return stats

    def print_summary(self):
        """Print a summary of all email lists."""
        stats = self.get_statistics()

        print("Email List Manager Summary")
        print("=" * 40)

        for list_name, stat in stats.items():
            print(f"\\nList: {list_name}")
            print(f"  Total addresses: {stat['total_addresses']}")
            print(f"  With display names: {stat['with_display_name']}")
            print(f"  Unique domains: {stat['unique_domains']}")

            if stat['top_domains']:
                print("  Top domains:")
                for domain, count in stat['top_domains']:
                    print(f"    {domain}: {count}")

# Usage example
def demo_email_list_manager():
    manager = EmailListManager()

    # Create lists and add addresses
    manager.add_to_list("customers", "john@example.com")
    manager.add_to_list("customers", "Jane Doe <jane@company.org>")
    manager.add_to_list("customers", "support@example.com")

    manager.add_to_list("staff", "admin@company.org")
    manager.add_to_list("staff", "hr@company.org")

    # Merge lists
    manager.merge_lists("customers", "staff", "all_contacts")

    # Print summary
    manager.print_summary()

    # Export to CSV
    manager.export_list_to_csv("all_contacts", "all_contacts.csv")
    print("\\nExported all_contacts to CSV file")

demo_email_list_manager()
```

### Integration with Email Processing

```python
from EMLMailReader import MailReader, MailAddressCollection

def extract_mailing_list(eml_files):
    """Extract all unique email addresses from multiple EML files."""

    all_addresses = MailAddressCollection()
    seen_emails = set()

    reader = MailReader()

    for eml_file in eml_files:
        try:
            message = reader.get_email(eml_file)

            if message:
                # Collect addresses from all fields
                collections = [
                    message.To,
                    message.Cc,
                    message.Bcc,
                    message.ReplyTo
                ]

                # Add From address
                if message.From:
                    temp_collection = MailAddressCollection()
                    temp_collection.append(message.From)
                    collections.append(temp_collection)

                # Process all collections
                for collection in collections:
                    for address in collection.export_as_list():
                        email_lower = address.Email.lower()
                        if email_lower not in seen_emails:
                            seen_emails.add(email_lower)
                            all_addresses.append(address)

        except Exception as e:
            print(f"Error processing {eml_file}: {e}")

    return all_addresses

def create_reply_all_list(message):
    """Create a reply-all recipient list from a message."""

    reply_list = MailAddressCollection()

    # Add original sender (from Reply-To if available, otherwise From)
    if message.ReplyTo.length() > 0:
        for address in message.ReplyTo.export_as_list():
            reply_list.append(address)
    elif message.From:
        reply_list.append(message.From)

    # Add all original recipients except current user
    # (In a real implementation, you'd filter out the current user's address)
    for collection in [message.To, message.Cc]:
        for address in collection.export_as_list():
            reply_list.append(address)

    return reply_list

# Usage
eml_files = ["/path/to/email1.eml", "/path/to/email2.eml"]
mailing_list = extract_mailing_list(eml_files)
print(f"Extracted {mailing_list.length()} unique email addresses")
```

## Best Practices

### 1. Use export_as_list() for Iteration

```python
# Recommended way to iterate
for address in collection.export_as_list():
    print(address.Email)

# Don't try to access internal list directly
```

### 2. Check Collection Length Before Processing

```python
if collection.length() > 0:
    # Process addresses
    for address in collection.export_as_list():
        # Handle each address
        pass
else:
    print("No addresses in collection")
```

### 3. Handle Duplicates When Merging

```python
def add_unique_address(collection, new_address):
    """Add address only if not already present."""

    for existing in collection.export_as_list():
        if existing.Email.lower() == new_address.Email.lower():
            return False  # Already exists

    collection.append(new_address)
    return True
```

### 4. Validate Addresses Before Adding

```python
import re

def add_validated_address(collection, email_string):
    """Add address only if email format is valid."""

    address = MailAddress()
    address.parse(email_string)

    # Basic email validation
    if re.match(r'^[^@]+@[^@]+\.[^@]+$', address.Email):
        collection.append(address)
        return True

    return False
```

## Related Classes

- [MailAddress](MailAddress.md) - Individual email address representation
- [RxMailMessage](RxMailMessage.md) - Email message using MailAddressCollection for recipients
- [MailReader](MailReader.md) - Parser that creates MailAddressCollection instances
