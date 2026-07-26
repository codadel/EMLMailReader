![EMLMailReader logo](https://static.citadelofcode.com/emlmailreader/logo.png)

[![PyPI version](https://img.shields.io/pypi/v/EMLMailReader.svg)](https://pypi.org/project/EMLMailReader/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Powered by Codadel](https://img.shields.io/badge/powered_by-Codadel-orange)](https://github.com/codadel)

# EMLMailReader

EMLMailReader is a dependency-free Python library for parsing EML files and
in-memory Internet messages. It produces a structured message and MIME tree,
preserves source bytes and ordered headers, decodes message content, and
reports recoverable syntax problems through diagnostics.

The parser provides receiver-oriented support for RFC 5322, RFC 6854, MIME,
RFC 2183, RFC 2231, and internationalized headers from RFC 6532.

## Features

- Parse EML files, bytes, strings, and binary or text streams
- Preserve raw source bytes, raw bodies, duplicate headers, and header order
- Parse mailboxes and named or empty address groups into structured values
- Decode encoded headers, Base64, quoted-printable, and text charsets
- Traverse nested MIME messages through one consistent `RxMailMessage` model
- Access plain-text bodies, HTML bodies, attachments, and inline resources
- Parse dates, message IDs, resent blocks, trace blocks, and MIME metadata
- Choose modern, lenient, or strict parsing behavior
- Apply configurable size, header, MIME-depth, part-count, and decoded-body limits
- Export the complete canonical message schema as a dictionary or JSON

## Requirements and installation

- Python 3.12 or newer
- No runtime dependencies outside the Python standard library

```bash
python -m pip install emlmailreader
```

## Parse an EML file

```python
from EMLMailReader import MailReader

message = MailReader().get_email("/path/to/message.eml")
if message is None:
    raise RuntimeError("The file was missing, empty, or could not be read")

print(message.Subject)
print([mailbox.Email for mailbox in message.From.Mailboxes])
print([mailbox.Email for mailbox in message.To.Mailboxes])
print(message.TextBody)
print(message.HtmlBody)
```

`get_email()` is the filesystem entry point. It returns `None` for missing,
empty, or unreadable files. A standards error still raises when strict parsing
is enabled.

## Parse in-memory input

Unit tests and applications that already have message content can avoid file
handling:

```python
from io import BytesIO

from EMLMailReader import MailReader

reader = MailReader()

from_bytes = reader.parse_bytes(
    b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
    b"From: Alice <alice@example.com>\r\n"
    b"To: Team: Bob <bob@example.com>, Carol <carol@example.com>;\r\n"
    b"Subject: Example\r\n\r\n"
    b"Hello"
)
from_text = reader.parse_string(
    "From: alice@example.com\r\n"
    "Subject: UTF-8 example – café\r\n\r\n"
    "Hello"
)
from_stream = reader.parse_stream(BytesIO(from_bytes.RawSource))
```

Use `parse_bytes()` when exact wire-byte preservation matters.
`parse_string()` encodes input as UTF-8 by default. `parse_stream()` reads a
binary or text stream from its current position.

## Addresses and headers

`From`, `Sender`, `ReplyTo`, `To`, `Cc`, and `Bcc` are `AddressList` values.
Their `Mailboxes` property provides a flattened immutable mailbox view, while
iteration over the address list retains group boundaries.

```python
for mailbox in message.From.Mailboxes:
    print(mailbox.DisplayName, mailbox.Email)

# Ordered, duplicate-preserving, and case-insensitive header access.
subject = message.Headers.get("subject")
received = message.Headers.get_all("Received", decoded=False)
subject_fields = message.Headers.occurrences("Subject")
```

Each header occurrence retains its raw, unfolded, decoded, position, and syntax
status values.

## MIME bodies and attachments

Every node in `Children` is another `RxMailMessage`. Attachments and inline
resources are immutable recursive tuple views of those same MIME nodes; there
are no separate attachment or collection classes.

```python
def walk(part):
    yield part
    for child in part.Children:
        yield from walk(child)


for part in walk(message):
    print(part.ContentType.MediaType, part.Name)

for attachment in message.Attachments:
    print(
        attachment.Name,
        attachment.ContentType.MediaType,
        len(attachment.DecodedBody),
    )

message.save_attachments("/existing/output/directory")
```

The attachment destination must already exist. Saved names are reduced to
their basename to prevent path traversal.

## Parsing modes, diagnostics, and limits

Modern and lenient modes retain recoverable messages and attach
`ParseDiagnostic` objects to the affected MIME node. Strict mode raises
`StandardsComplianceError` when error diagnostics are present.

```python
from EMLMailReader import (
    MailReader,
    ParserLimits,
    ParsingMode,
    StandardsComplianceError,
)

reader = MailReader(
    parsing_mode=ParsingMode.STRICT,
    limits=ParserLimits(
        max_message_bytes=25 * 1024 * 1024,
        max_header_bytes=512 * 1024,
        max_header_count=5_000,
        max_mime_depth=30,
        max_parts=2_000,
        max_decoded_part_bytes=10 * 1024 * 1024,
    ),
)

try:
    message = reader.get_email("message.eml")
except StandardsComplianceError as error:
    for diagnostic in error.diagnostics:
        print(diagnostic.severity.value, diagnostic.code, diagnostic.message)
```

For non-strict parsing, diagnostics are available from
`message.Diagnostics`; nested-part diagnostics remain on their corresponding
child nodes.

## Export the canonical schema

The current major-version API exposes one model and one structured JSON schema.

```python
data = message.to_dict()
json_text = message.export_as_json()

assert data["schema_version"] == 2
```

The schema includes structured headers, addresses, dates, identifiers, MIME
metadata, child parts, derived bodies, and diagnostics.

## Logging

Logging is disabled by default. It can be routed through Python's standard
logging system to the console or to a timestamped file:

```python
from EMLMailReader import LoggingMode, MailReader

console_reader = MailReader(logging_mode=LoggingMode.CONSOLE)
file_reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder="/existing/log/directory",
)
```

## Development and testing

The test suite uses `pytest` and keeps unit and functional responsibilities
separate:

- `tests/unit/` uses hard-coded, in-memory fixtures and performs no file handling.
- `tests/functional/` parses real EML files and exercises filesystem behavior.
- `tests/functional/assets/` contains EML assets used only by functional tests.

With [mise](https://mise.jdx.dev/) installed:

```bash
mise run setup
mise run unit
mise run functional
mise run test
mise run test-verbose
mise run coverage
mise run coverage-html
```

The coverage tasks measure branch coverage for `EMLMailReader` and enforce a
minimum of 95%.

The equivalent direct commands are:

```bash
pytest tests/unit
pytest tests/functional
pytest
pytest --cov=EMLMailReader --cov-branch --cov-report=term-missing --cov-fail-under=95
```

## Documentation

The [documentation index](docs/index.md) links to the public API reference:

- [MailReader](docs/MailReader.md)
- [RxMailMessage](docs/RxMailMessage.md)
- [AddressList](docs/AddressList.md)
- [Structured types](docs/StructuredTypes.md)
- [Enumerations](docs/Enumerations.md)
- [Exceptions](docs/Exceptions.md)

## License

EMLMailReader is distributed under the terms in [LICENSE](LICENSE).

## Support

Report issues and feature requests in the
[GitHub issue tracker](https://github.com/codadel/EMLMailReader/issues).
