# EMLMailReader API patterns

## Select an input API

| Input | API | Contract |
| --- | --- | --- |
| EML path | `MailReader.get_email(path)` | Returns `None` for missing, empty, or unreadable files |
| Wire bytes | `MailReader.parse_bytes(source)` | Preserves exact root bytes in `RawSource` |
| Message text | `MailReader.parse_string(source)` | Encodes with UTF-8 unless another encoding is supplied |
| Open stream | `MailReader.parse_stream(stream)` | Reads from the current position and leaves the stream open |

Keep filesystem handling out of code that already has the message in memory.
Allow `StandardsComplianceError` to remain distinguishable from file failures.

## Configure a reader

```python
from EMLMailReader import MailReader, ParserLimits, ParsingMode

reader = MailReader(
    parsing_mode=ParsingMode.MODERN,
    limits=ParserLimits(
        max_message_bytes=25 * 1024 * 1024,
        max_header_bytes=512 * 1024,
        max_header_count=5_000,
        max_mime_depth=30,
        max_parts=2_000,
        max_decoded_part_bytes=10 * 1024 * 1024,
    ),
)
```

Treat these values as an example, not a universal recommendation. Choose them
from expected message and attachment sizes.

## Read structured fields

```python
sender_addresses = [item.Email for item in message.From.Mailboxes]
recipient_addresses = [item.Email for item in message.To.Mailboxes]
received_values = message.Headers.get_all("Received", decoded=False)
subject_occurrences = message.Headers.occurrences("Subject")
```

Iterate an `AddressList` directly when group boundaries matter. Use
`.Mailboxes` for a flattened immutable mailbox view.

Use structured `Date`, `MessageID`, `InReplyTo`, `References`, `ResentBlocks`,
and `TraceBlocks` values. Do not recreate them from raw strings.

## Select content

- Use `TextBody` for the first plain-text body in the subtree.
- Use `HtmlBody` for the first HTML body in the subtree.
- Use `Body` for the parser's preferred decoded body.
- Use `RawBody` for pre-transfer-decoding bytes.
- Use `DecodedBody` for a leaf's transfer-decoded bytes.
- Traverse `Children` when MIME placement or nesting matters.

The library does not convert HTML into plain text.

## Inspect attachments without writing files

```python
attachment_rows = [
    {
        "name": part.Name,
        "media_type": part.ContentType.MediaType,
        "size": len(part.DecodedBody),
        "content_id": part.ContentID.value if part.ContentID else None,
    }
    for part in message.Attachments
]
```

Check the installed structured type before assuming an attribute name beyond
the documented public surface. Save attachments only when the user needs files
on disk.

## Serialize

Use `message.to_dict()` for a Python mapping and `message.export_as_json()` for
JSON text. The canonical recursive schema has `schema_version` set to `2`.
Raw byte payloads and duplicate attachment projections are intentionally
omitted.
