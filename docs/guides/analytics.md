# Build analytics records

The library object model is useful for inspection, but an analytics dataset is
usually easier to work with when each email becomes a plain dictionary with a
stable schema.

## Create one record

```python
from pathlib import Path

from EMLMailReader import MailReader


def address_values(collection):
    return [
        {
            "display_name": address.DisplayName or None,
            "email": address.Email or None,
        }
        for address in collection.export_as_list()
    ]


def parse_record(reader, eml_path):
    message = reader.get_email(str(eml_path))
    if message is None:
        return None

    return {
        "source_file": str(eml_path),
        "message_id": message.MessageID or None,
        "subject": message.Subject or None,
        "date_raw": message.Date or None,
        "from": (
            {
                "display_name": message.From.DisplayName or None,
                "email": message.From.Email or None,
            }
            if message.From is not None
            else None
        ),
        "to": address_values(message.To),
        "cc": address_values(message.Cc),
        "bcc": address_values(message.Bcc),
        "reply_to": address_values(message.ReplyTo),
        "body": message.Body,
        "is_multipart": message.IsMultiPart,
        "attachment_count": message.Attachments.length(),
        "headers": dict(message.Headers),
    }


reader = MailReader()
record = parse_record(reader, Path("mail/example.eml"))
```

This schema keeps the original file path, preserves multiple recipients, and
uses `None` consistently for missing scalar values.

## Normalize dates deliberately

v1 leaves the `Date` header as a string. Python's standard library can parse
many valid mail dates, but real datasets may contain invalid values.

```python
from email.utils import parsedate_to_datetime


def parse_date(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
```

Keep `date_raw` even when you add a normalized date. That makes failed
conversions auditable.

## Store attachment metadata without bytes

Binary contents can make analytics records unnecessarily large. Extract only
the metadata you need:

```python
attachment_rows = [
    {
        "name": attachment.Name or None,
        "media_type": attachment.ContentType.MediaType,
        "size_bytes": len(attachment.Contents),
        "content_id": attachment.ContentID or None,
    }
    for attachment in message.Attachments.export_as_list()
]
```

## Keep parse failures as data

Do not silently discard a `None` result. Record the source file and failure so
you can measure data quality and retry problem files after upgrading the
parser.

```python
if record is None:
    failure = {
        "source_file": "mail/example.eml",
        "status": "parse_failed",
    }
```

Enable console or file logging when you need diagnostic text alongside that
failure record.
