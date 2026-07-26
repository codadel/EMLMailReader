# EMLMailReader

EMLMailReader parses Internet message files into a structured message and MIME
tree. It preserves original bytes and headers, decodes text and transfer
encodings, exposes addresses and message identifiers as typed values, and
records parser diagnostics without discarding recoverable mail.

The current API uses one canonical model. Attachments and inline resources are
`RxMailMessage` MIME parts; there are no separate attachment or collection
classes.

## Requirements and installation

- Python 3.12 or newer
- No runtime dependencies outside the Python standard library
- Inline type information for PEP 561-aware static type checkers

```bash
python -m pip install emlmailreader
```

## Parse an EML file

```python
from EMLMailReader import MailReader

message = MailReader().get_email("message.eml")
if message is None:
    raise RuntimeError("The file was missing, empty, or could not be read")

print(message.Subject)
print([mailbox.Email for mailbox in message.From.Mailboxes])
print(message.TextBody)
print(message.HtmlBody)
```

`get_email()` is the filesystem entry point. It returns `None` for missing,
empty, or unreadable files. In strict parsing mode, syntax errors raise
`StandardsComplianceError`.

## Parse in-memory input

```python
from io import BytesIO

from EMLMailReader import MailReader

reader = MailReader()

from_bytes = reader.parse_bytes(
    b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
    b"From: alice@example.com\r\n"
    b"Subject: Example\r\n\r\n"
    b"Hello"
)
from_text = reader.parse_string(
    "Date: Fri, 21 Nov 1997 09:55:06 -0600\r\nFrom: alice@example.com\r\n\r\nHello"
)
from_stream = reader.parse_stream(BytesIO(from_bytes.RawSource))
```

Use `parse_bytes()` when wire-byte preservation matters. `parse_string()`
encodes the input as UTF-8 by default, and `parse_stream()` accepts a binary or
text stream at its current position.

## Work with the MIME tree

Each node in `message.Children` is another `RxMailMessage`.

```python
def walk(part):
    yield part
    for child in part.Children:
        yield from walk(child)


for part in walk(message):
    print(part.ContentType.MediaType, part.Name)

for attachment in message.Attachments:
    print(attachment.Name, len(attachment.DecodedBody))
```

`Attachments` and `InlineResources` are recursive, immutable tuple views over
the same MIME nodes already present in `Children`.

## Inspect diagnostics

Receiver modes return recoverable input and attach diagnostics to the affected
MIME node.

```python
for diagnostic in message.Diagnostics:
    print(diagnostic.severity.value, diagnostic.code, diagnostic.message)
```

Diagnostics on nested parts are stored on those child nodes. See
[Structured types](StructuredTypes.md) for strict mode, resource limits, and
diagnostic metadata.

## Save attachments

```python
message.save_attachments("/existing/output/directory")
```

The destination directory must already exist. Saved names are reduced to their
basename to prevent path traversal. See [RxMailMessage](RxMailMessage.md) for
collision and fallback-name behavior.

## API reference

### Parsing and message model

- [MailReader](MailReader.md)
- [RxMailMessage](RxMailMessage.md)
- [Structured types](StructuredTypes.md)

### Addresses and MIME headers

- [MailAddress](MailAddress.md)
- [AddressList](AddressList.md)
- [ContentType](ContentType.md)
- [ContentDisposition](ContentDisposition.md)

### Utilities

- [TextEncoding](TextEncoding.md)
- [Logger](Logger.md)
- [Enumerations](Enumerations.md)
- [Exceptions](Exceptions.md)

## Public package imports

The documented classes are exported from `EMLMailReader`, except
`LoggingLevel`, which is available from `EMLMailReader.Enumerations`.

```python
from EMLMailReader import (
    AddressList,
    ContentDisposition,
    ContentType,
    MailAddress,
    MailReader,
    ParserLimits,
    ParsingMode,
    RxMailMessage,
)
```
