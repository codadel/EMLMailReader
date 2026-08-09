# Parse email without flattening away useful structure

EMLMailReader v2 turns an EML file or in-memory Internet message into a typed,
recursive Python model. It preserves the source bytes and ordered headers,
decodes text and transfer encodings, exposes structured addresses and message
identifiers, and reports recoverable standards problems as diagnostics.

!!! info "You are reading the v2 documentation"

    These pages describe the EMLMailReader 2.x API. Use the version selector to
    open the frozen v1.0.4 documentation.

## Install

EMLMailReader requires Python 3.12 or newer and has no runtime dependencies
outside the Python standard library.

```console
python -m pip install "emlmailreader>=2,<3"
```

## Parse a message

```python
from EMLMailReader import MailReader

message = MailReader().get_email("/data/mail/example.eml")
if message is None:
    raise RuntimeError("The file was missing, empty, or unreadable")

print(message.Subject)
print([mailbox.Email for mailbox in message.From.Mailboxes])
print(message.TextBody)
```

Use `parse_bytes()`, `parse_string()`, or `parse_stream()` when the message is
already in memory. Prefer bytes when exact source preservation matters.

## What v2 adds

- ordered, duplicate-preserving headers with raw and decoded values;
- structured mailboxes, named groups, and empty groups;
- parsed dates, message identifiers, resent blocks, and trace blocks;
- one recursive `RxMailMessage` model for the root and every MIME entity;
- raw, transfer-decoded, plain-text, and HTML body views;
- MIME metadata for attachments, inline resources, partial messages, and
  external bodies;
- modern, lenient, and strict parsing modes;
- stable diagnostics with optional RFC, header, line, and column context;
- configurable message, header, MIME-depth, part-count, and decoded-body
  limits; and
- a canonical recursive JSON-compatible schema.

## Choose a path

- [Install and verify v2](getting-started/installation.md).
- [Parse your first message](getting-started/first-email.md).
- [Understand the message model](getting-started/message-model.md).
- [Build analytics records](guides/analytics.md).
- [Process a directory safely](guides/batch-processing.md).
- [Migrate code from v1](migration/v1-to-v2.md).
- Open the [API reference](reference/index.md) for exact types and methods.
