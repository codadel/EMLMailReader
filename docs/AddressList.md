# AddressList

`AddressList` represents a complete RFC-style address header value. It retains
both individual `MailAddress` objects and named or empty `AddressGroup`
objects. `RxMailMessage.From`, `Sender`, `ReplyTo`, `To`, `Cc`, and `Bcc` all
use this type.

## Constructor and parsing

```python
AddressList(raw_value: str = "")
```

Supplying a value parses it immediately.

```python
from EMLMailReader import AddressList

recipients = AddressList(
    "Alice <alice@example.com>, "
    "Engineering: Bob <bob@example.com>, carol@example.com;"
)
```

An existing object can be reused:

```python
recipients.parse("Undisclosed recipients:;")
```

```python
parse(value: str) -> AddressList
```

`parse()` replaces `RawValue` and `Items`, then returns the same object.

## Properties

| Property | Type | Description |
| --- | --- | --- |
| `RawValue` | `str` | Complete input header value |
| `Items` | `list[MailAddress \| AddressGroup]` | Top-level mailboxes and groups |
| `Mailboxes` | `tuple[MailAddress, ...]` | Flattened immutable view of every group member and standalone mailbox |

`AddressGroup` is an exported frozen data class with:

| Field | Type |
| --- | --- |
| `display_name` | `str` |
| `addresses` | `tuple[MailAddress, ...]` |
| `raw_value` | `str` |

```python
from EMLMailReader import AddressGroup

for item in recipients:
    if isinstance(item, AddressGroup):
        print(item.display_name)
        for mailbox in item.addresses:
            print(mailbox.Email)
    else:
        print(item.Email)
```

## Collection behavior

`AddressList` supports:

- iteration over top-level `Items`
- `len(addresses)` for the number of top-level items
- truth testing

Truth testing is true when parsed items exist or a non-empty raw value was
supplied. `len()` does not return the flattened mailbox count; use
`len(addresses.Mailboxes)` for that.

## Formatting

```python
value = recipients.to_header_value()
same_value = str(recipients)
```

Named and empty groups are serialized with group syntax. Individual addresses
delegate to `MailAddress.to_header_value()`.

## Serialization

```python
data = recipients.to_dict()
```

The result is a list. Each entry has a discriminator:

```python
[
    {
        "type": "mailbox",
        "display_name": "Alice",
        "email": "alice@example.com",
        "local_part": "alice",
        "domain": "example.com",
        "raw_value": "Alice <alice@example.com>",
        "internationalized": False,
    },
    {
        "type": "group",
        "display_name": "Engineering",
        "addresses": [
            {
                "display_name": "Bob",
                "email": "bob@example.com",
                "local_part": "bob",
                "domain": "example.com",
                "raw_value": "Bob <bob@example.com>",
                "internationalized": False,
            },
            {
                "display_name": "",
                "email": "carol@example.com",
                "local_part": "carol",
                "domain": "example.com",
                "raw_value": "carol@example.com",
                "internationalized": False,
            },
        ],
        "raw_value": (
            "Alice <alice@example.com>, "
            "Engineering: Bob <bob@example.com>, carol@example.com;"
        ),
    },
]
```

## Related pages

- [MailAddress](MailAddress.md)
- [RxMailMessage](RxMailMessage.md)
- [Structured types](StructuredTypes.md)
