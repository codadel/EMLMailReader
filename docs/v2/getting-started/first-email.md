# Parse your first message

## Read a file

```python
from pathlib import Path

from EMLMailReader import MailReader

path = Path("/data/mail/example.eml")
message = MailReader().get_email(str(path))

if message is None:
    raise RuntimeError(f"Could not read {path}")

print(message.Subject)
print(message.Date.value if message.Date else None)
print([mailbox.Email for mailbox in message.From.Mailboxes])
print([mailbox.Email for mailbox in message.To.Mailboxes])
```

`get_email()` returns `None` when a file is missing, empty, or cannot be read.
Strict standards failures are different: they raise `StandardsComplianceError`.

## Parse bytes already in memory

```python
from EMLMailReader import MailReader

source = (
    b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
    b"From: Alice <alice@example.com>\r\n"
    b"To: Analytics: Bob <bob@example.com>, Carol <carol@example.com>;\r\n"
    b"Subject: Weekly metrics\r\n"
    b"Message-ID: <weekly-42@example.com>\r\n"
    b"\r\n"
    b"The report is attached."
)

message = MailReader().parse_bytes(source)

assert message.RawSource == source
print(message.MessageID.value if message.MessageID else None)
print(message.Body)
```

`parse_bytes()` always returns an `RxMailMessage` unless strict parsing raises.
It is the best input method when exact wire bytes are important.

## Other input forms

```python
from io import BytesIO, StringIO

from EMLMailReader import MailReader

reader = MailReader()
from_text = reader.parse_string("From: a@example.com\r\n\r\nHello")
from_binary_stream = reader.parse_stream(BytesIO(source))
from_text_stream = reader.parse_stream(StringIO("From: a@example.com\n\nHello"))
```

Text input is encoded as UTF-8 before parsing. The caller retains ownership of
streams and must close them.

## Check diagnostics

```python
for diagnostic in message.Diagnostics:
    print(
        diagnostic.severity.value,
        diagnostic.code,
        diagnostic.header,
        diagnostic.message,
    )
```

Diagnostics from nested MIME parts remain on their corresponding child nodes.
See [Parsing modes, diagnostics, and limits](../concepts/parser-modes.md).
