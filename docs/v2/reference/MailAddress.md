# MailAddress

`MailAddress` stores one mailbox with its display name and address components.
Parsed message header properties expose mailboxes through `AddressList`.

## Properties

| Property | Type | Description |
| --- | --- | --- |
| `DisplayName` | `str` | Decoded human-readable name |
| `Email` | `str` | Complete address specification |
| `LocalPart` | `str` | Portion before `@` |
| `Domain` | `str` | Portion after `@` |
| `RawValue` | `str` | Source value supplied to `parse()` |
| `IsInternationalized` | `bool` | True when the source contains non-ASCII characters |

All properties default to an empty string except `IsInternationalized`, which
defaults to `False`.

## Parsing

```python
from EMLMailReader import MailAddress

address = MailAddress()
address.parse("Alice Example <alice@example.com>")

assert address.DisplayName == "Alice Example"
assert address.Email == "alice@example.com"
assert address.LocalPart == "alice"
assert address.Domain == "example.com"
```

```python
parse(MailAddressString: str) -> None
```

`parse()` resets the instance, parses the first mailbox in the supplied value,
and decodes an encoded display name. If structured parsing fails, it falls back
to a simple mailbox/display-name split.

For complete `To`, `From`, and similar header values, use `AddressList` so
additional mailboxes and groups are not discarded.

## Constructing from components

```python
address = MailAddress.from_parts(
    display_name="Alice Example",
    username="alice",
    domain="example.com",
)
```

```python
from_parts(
    display_name: str,
    username: str,
    domain: str,
    raw_value: str = "",
) -> MailAddress
```

This class method is used by `AddressList` and is also available to callers.

## Formatting and serialization

```python
header_value = address.to_header_value()
same_value = str(address)
data = address.to_dict()
```

`to_header_value()` and `str(address)` use Python's header registry to quote or
format the display name where possible.

`to_dict()` returns:

```python
{
    "display_name": "Alice Example",
    "email": "alice@example.com",
    "local_part": "alice",
    "domain": "example.com",
    "raw_value": "Alice Example <alice@example.com>",
    "internationalized": False,
}
```

## Related pages

- [AddressList](AddressList.md)
- [RxMailMessage](RxMailMessage.md)
