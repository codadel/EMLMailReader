# Process a directory of EML files

Reuse one configured `MailReader` across files and record failures separately
from successfully parsed messages.

```python
from collections.abc import Iterator
from pathlib import Path

from EMLMailReader import MailReader, ParserLimits, RxMailMessage


def read_mailbox(root: Path) -> Iterator[tuple[Path, RxMailMessage]]:
    reader = MailReader(
        limits=ParserLimits(
            max_message_bytes=25 * 1024 * 1024,
            max_mime_depth=30,
            max_parts=2_000,
        )
    )

    for path in sorted(root.rglob("*.eml")):
        message = reader.get_email(str(path))
        if message is not None:
            yield path, message


for path, message in read_mailbox(Path("/data/export")):
    print(path, message.Subject, len(message.Attachments))
```

## Operational recommendations

- Treat `None` as a file-read outcome, not an empty parsed message.
- Store the source path or another stable ingestion identifier.
- Apply explicit limits before processing external mailboxes.
- Aggregate diagnostic codes and severities rather than logging entire
  messages.
- Avoid loading a directory's complete parsed result set into memory when a
  generator or streaming write is sufficient.
- Decide how duplicate input files will be detected before rerunning a batch.

Use strict mode for validation jobs that should reject nonconformant input. For
analytics, modern mode usually retains more useful evidence.
