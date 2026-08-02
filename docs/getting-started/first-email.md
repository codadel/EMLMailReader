# Parse your first email

`MailReader` accepts the path to one EML file and returns an `RxMailMessage` or
`None`.

## Read a message

```python
from pathlib import Path

from EMLMailReader import MailReader

eml_path = Path("mail/example.eml")
reader = MailReader()
message = reader.get_email(str(eml_path))

if message is None:
    raise RuntimeError(f"Could not parse {eml_path}")

print(f"Subject: {message.Subject}")
print(f"Date: {message.Date}")
print(f"From: {message.From}")
print(f"To: {message.To}")
print(f"Body: {message.Body}")
```

!!! important "Check for `None`"

    In v1, file and parse errors are caught inside `get_email()`. The method
    logs the diagnostic when logging is enabled and returns `None` to the
    caller.

## Access structured addresses

`From` is either a `MailAddress` or `None`. Recipient fields are
`MailAddressCollection` objects.

```python
sender_email = message.From.Email if message.From is not None else None

to_addresses = [
    address.Email
    for address in message.To.export_as_list()
]

print(sender_email)
print(to_addresses)
```

## Inspect attachments

```python
print(f"Attachment count: {message.Attachments.length()}")

for attachment in message.Attachments.export_as_list():
    print(attachment.Name)
    print(attachment.ContentType.MediaType)
    print(len(attachment.Contents))
```

Attachment contents are already decoded into `bytes` and held in memory.

## Turn on diagnostics

```python
from EMLMailReader import LoggingMode, MailReader

reader = MailReader(logging_mode=LoggingMode.CONSOLE)
message = reader.get_email("mail/example.eml")
```

Console logging is useful when a parse returns `None` or a malformed section is
ignored. For production analytics, also record the source path and whether the
parse succeeded.

## Next step

Read [Understand the message model](message-model.md) before designing your
analytics schema.
