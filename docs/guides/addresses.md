# Work with addresses

## Sender

`message.From` is a `MailAddress` when a From header was parsed, otherwise it is
`None`.

```python
if message.From is None:
    sender = None
else:
    sender = {
        "display_name": message.From.DisplayName or None,
        "email": message.From.Email or None,
    }
```

## Recipient collections

`To`, `Cc`, `Bcc`, and `ReplyTo` are always `MailAddressCollection` objects.

```python
print(message.To.length())

for address in message.To.export_as_list():
    print(address.DisplayName)
    print(address.Email)
```

`export_as_list()` returns a deep copy. It is safe to transform the returned
objects without altering the message's internal collection.

## Display values

```python
print(str(message.From))
print(str(message.To))
```

A `MailAddress` renders as `Display Name <user@example.com>` when it has a
display name. A collection renders as a semicolon-separated string.

For analytics, retain structured email and display-name fields rather than
using the combined string.

## Parse an address directly

```python
from EMLMailReader import MailAddress

address = MailAddress()
address.parse('"Example User" <user@example.com>')

assert address.DisplayName == "Example User"
assert address.Email == "user@example.com"
```

The v1 parser handles common mailbox forms. It is not a complete RFC mailbox
parser; see [v1 behavior and limitations](../concepts/v1-behavior.md) before
using it for validation or security decisions.
