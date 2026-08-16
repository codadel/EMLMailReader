# Process a folder of emails

Reuse one `MailReader` to process files sequentially. Preserve the path and
outcome for every input so failed parses do not disappear from the dataset.

```python
from pathlib import Path

from EMLMailReader import MailReader


def parse_folder(root):
    reader = MailReader()
    messages = []
    failures = []

    for eml_path in sorted(Path(root).rglob("*.eml")):
        message = reader.get_email(str(eml_path))
        if message is None:
            failures.append(str(eml_path))
            continue

        messages.append(
            {
                "source_file": str(eml_path),
                "message": message,
            }
        )

    return messages, failures


messages, failures = parse_folder("mail-export")
print(f"Parsed: {len(messages)}")
print(f"Failed: {len(failures)}")
```

## Produce newline-delimited JSON

For larger collections, write one record at a time instead of holding every
record in a list:

```python
import json
from pathlib import Path

from EMLMailReader import MailReader

reader = MailReader()

with Path("messages.ndjson").open("w", encoding="utf-8") as output:
    for eml_path in sorted(Path("mail-export").rglob("*.eml")):
        message = reader.get_email(str(eml_path))
        if message is None:
            continue

        record = json.loads(message.export_as_json())
        record["Source-File"] = str(eml_path)
        output.write(json.dumps(record, ensure_ascii=False) + "\n")
```

`export_as_json()` omits the body and attachment bytes. Build a custom record
as shown in [Build analytics records](analytics.md) when those fields are
required.

## Operational guidance

- v1 reads each file and decoded attachment content into memory. Process files
  sequentially and enforce file-size limits before parsing untrusted input.
- Store failures separately and enable logging for a diagnostic run.
- Avoid sharing one `MailReader` across concurrent threads. v1 does not define
  a thread-safety contract.
- Treat message bodies, headers, filenames, and addresses as untrusted data.
- Do not log body text or recipient data unless your privacy policy permits it.
