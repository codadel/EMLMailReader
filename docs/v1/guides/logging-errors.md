# Logging and failures

## Failure contract

`MailReader.get_email()` catches file-access and parse exceptions internally.
It returns:

- an `RxMailMessage` when it can produce a result; or
- `None` when the file is missing, unreadable, empty, or parsing fails before a
  result can be produced.

```python
message = reader.get_email("mail/example.eml")
if message is None:
    print("Parse failed")
```

Do not rely on catching `FileMissingError` around `get_email()` in v1; the
method handles that exception before returning.

## Console logging

```python
from EMLMailReader import LoggingMode, MailReader

reader = MailReader(logging_mode=LoggingMode.CONSOLE)
message = reader.get_email("mail/example.eml")
```

## File logging

The target directory must already exist:

```python
from pathlib import Path

from EMLMailReader import LoggingMode, MailReader

log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)

reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder=str(log_dir),
)
```

An unavailable log directory raises `FolderNotAvailableError` while the reader
is being constructed.

## Exceptions from other operations

| Operation | Relevant behavior |
| --- | --- |
| `get_email()` | Catches errors, logs them, and returns `None` |
| `save_attachments()` | Raises `FolderNotAvailableError` when the target path does not exist |
| `Logger.set_configuration()` | Raises `FolderNotAvailableError` for an invalid file-log directory |
| `TextEncoding.decode_header()` | Can raise `InvalidEncodingError` when called directly with an unsupported encoded-word method |

## Logging caveats

v1 configures Python's process-wide `logging` module with `basicConfig()`.
Applications that already configure logging should create the reader after
their own logging setup and verify the resulting handler behavior.

Avoid logging message bodies, raw headers, or addresses unless that data is
permitted by your privacy and retention policies.
