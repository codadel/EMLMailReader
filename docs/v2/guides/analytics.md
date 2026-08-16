# Build stable analytics records

Keep parsing separate from the record shape stored by an analytics system. A
small projection function makes schema decisions explicit and keeps raw email
objects out of dataframes or databases.

```python
from typing import Any

from EMLMailReader import RxMailMessage


def analytics_record(message: RxMailMessage, source_name: str) -> dict[str, Any]:
    return {
        "source": source_name,
        "subject": message.Subject,
        "sent_at": message.Date.value.isoformat()
        if message.Date and message.Date.value
        else None,
        "message_id": message.MessageID.value if message.MessageID else None,
        "from": [mailbox.Email for mailbox in message.From.Mailboxes],
        "to": [mailbox.Email for mailbox in message.To.Mailboxes],
        "cc": [mailbox.Email for mailbox in message.Cc.Mailboxes],
        "text": message.TextBody,
        "html_available": bool(message.HtmlBody),
        "attachment_count": len(message.Attachments),
        "attachments": [
            {
                "name": part.Name,
                "media_type": part.ContentType.MediaType,
                "decoded_bytes": len(part.DecodedBody),
            }
            for part in message.Attachments
        ],
        "diagnostic_codes": sorted(
            {item.code for item in recursive_diagnostics(message)}
        ),
    }


def recursive_diagnostics(message: RxMailMessage):
    yield from message.Diagnostics
    for child in message.Children:
        yield from recursive_diagnostics(child)
```

## Preserve groups when they matter

`AddressList.Mailboxes` is convenient for participant counts. Iterate over the
address list itself when named or empty groups are analytically significant.

## Treat text as untrusted data

Parsed bodies, display names, filenames, and subjects can contain sensitive or
hostile content. Escape values before rendering HTML, avoid logging message
bodies by default, and apply retention rules before storing raw source bytes.

## Choose the right export

- Use a custom projection for a stable analytics table.
- Use `to_dict()` when the complete canonical v2 schema is appropriate.
- Use `export_as_json()` when a serialized form of that schema is required.
