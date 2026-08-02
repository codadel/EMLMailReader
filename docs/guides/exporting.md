# Export parsed data

## Built-in JSON summary

`RxMailMessage.export_as_json()` returns a JSON string—not a dictionary.

```python
import json

summary = json.loads(message.export_as_json())
print(summary["Subject"])
```

The v1 summary contains these keys:

| Key | Source |
| --- | --- |
| `From` | Formatted sender string |
| `Subject` | Subject string |
| `Message-ID` | Message identifier |
| `IsMultiPart` | Multipart boolean |
| `Mime-Version` | MIME version string |
| `Date` | Original Date header string |
| `Headers` | Unmapped header dictionary |
| `Content-Type` | Formatted content type string |
| `To`, `Cc`, `Bcc`, `Reply-To` | Semicolon-separated address strings |
| `Attachment-Count` | Number of extracted attachments |

The summary excludes `Body`, `Children`, attachment metadata, and attachment
bytes.

## Prefer a stable application schema

For analytics, build a dictionary that represents your own data contract:

```python
record = {
    "message_id": message.MessageID or None,
    "subject": message.Subject or None,
    "date_raw": message.Date or None,
    "from_email": message.From.Email if message.From else None,
    "to_emails": [
        address.Email
        for address in message.To.export_as_list()
    ],
    "body": message.Body,
    "attachment_count": message.Attachments.length(),
}
```

This avoids depending on v1's capitalized JSON keys and lets you preserve lists
as arrays rather than semicolon-separated strings.

## Preserve source and parse status

The message object does not store the path it came from. Add it to every output
record yourself, along with a status for parse failures.

```python
result = {
    "source_file": str(eml_path),
    "status": "parsed" if message is not None else "parse_failed",
}
```
