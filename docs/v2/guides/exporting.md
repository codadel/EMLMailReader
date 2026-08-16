# Export parsed data

## Canonical dictionary

```python
record = message.to_dict()
assert record["schema_version"] == 2
```

The record contains structured headers, addresses, date and identifier values,
MIME metadata, derived text bodies, recursive children, and diagnostics.

Raw byte properties are deliberately excluded. This avoids accidental payload
duplication and keeps the result JSON-compatible.

## JSON text

```python
json_text = message.export_as_json()
```

The serializer preserves Unicode instead of forcing non-ASCII characters into
escape sequences.

## JSON Lines example

```python
from pathlib import Path

from EMLMailReader import MailReader

reader = MailReader()
with Path("messages.jsonl").open("w", encoding="utf-8") as output:
    for path in sorted(Path("/data/mail").glob("*.eml")):
        message = reader.get_email(str(path))
        if message is not None:
            output.write(message.export_as_json())
            output.write("\n")
```

For long-lived datasets, consider projecting a smaller application-owned
schema so library additions do not create unexpected columns.
