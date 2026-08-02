# Migrate from v1 to v2

EMLMailReader v2 replaces the flattened v1 model with one structured,
standards-aware message and MIME model. Treat the upgrade as a schema migration,
not a drop-in patch update.

## Package installation

```console
python -m pip install --upgrade "emlmailreader>=2,<3"
```

Pin v1 while migrating production code:

```console
python -m pip install "emlmailreader==1.0.4"
```

## Major API changes

| v1 | v2 |
| --- | --- |
| `MailAddressCollection` | `AddressList` |
| `MailAttachment` objects | Attachment `RxMailMessage` nodes |
| `MailAttachmentCollection` | Immutable `message.Attachments` tuple |
| dictionary-like flattened headers | Ordered `HeaderCollection` |
| string `Date` | `ParsedDateTime` or `None` |
| string `MessageID` | `ParsedMessageID` or `None` |
| enum-only transfer encoding | Lossless `TransferEncodingValue` |
| shallow JSON metadata | Recursive canonical schema version 2 |
| file-only parsing | Files, bytes, strings, and streams |
| limited failure information | Structured diagnostics and strict mode |

## Address collections

Before:

```python
recipients = message.To.export_as_list()
count = message.To.length()
```

After:

```python
recipients = message.To.Mailboxes
count = len(message.To)
emails = [mailbox.Email for mailbox in message.To.Mailboxes]
```

`len(message.To)` counts top-level mailboxes and groups. Use
`len(message.To.Mailboxes)` for the flattened mailbox count.

## Attachments

Before:

```python
for attachment in message.Attachments.export_as_list():
    print(attachment.Name, len(attachment.Contents))
```

After:

```python
for attachment in message.Attachments:
    print(attachment.Name, len(attachment.DecodedBody))
```

Attachments are no longer copied into parallel model classes. They are the
same MIME nodes found by traversing `Children`.

## Dates and identifiers

Before:

```python
sent_at = message.Date
identifier = message.MessageID
```

After:

```python
sent_at = message.Date.value if message.Date else None
raw_date = message.Date.raw_value if message.Date else None
identifier = message.MessageID.value if message.MessageID else None
```

Check `valid` when input quality matters.

## Headers

Before, repeated fields could be flattened or overwritten. In v2:

```python
last_subject = message.Headers.get("Subject")
all_received = message.Headers.get_all("Received", decoded=False)
subject_occurrences = message.Headers.occurrences("Subject")
```

Do not replace `HeaderCollection` with `dict(message.Headers)`; duplicate names
and order are part of the model.

## JSON export

Before:

```python
json_text = message.export_as_json()
```

The method still exists, but its output is intentionally different. v2 emits a
recursive record with `schema_version == 2`. Update warehouse schemas,
fixtures, and downstream transformations before switching production data.

## Parsing policy

Configure explicit limits and decide whether recoverable diagnostics are data
quality signals or hard failures:

```python
from EMLMailReader import MailReader, ParserLimits, ParsingMode

reader = MailReader(
    parsing_mode=ParsingMode.MODERN,
    limits=ParserLimits(max_message_bytes=25 * 1024 * 1024),
)
```

Use strict mode only when rejecting any error-level standards finding is the
desired application policy.

## Recommended migration sequence

1. Pin the existing production environment to v1.0.4.
2. Add v2 to a separate test environment.
3. Replace collection helper methods and attachment classes.
4. Update date, identifier, header, and JSON handling.
5. Add limits and diagnostic collection.
6. Compare analytics records from representative real mail.
7. Update stored schema documentation before changing production ingestion.
