# Handle logging and failures

## File-reading outcomes

`get_email()` returns `None` for missing, empty, or unreadable files. Parsing
bytes, strings, or streams does not use that sentinel.

## Standards failures

Strict mode raises `StandardsComplianceError`; its `diagnostics` tuple contains
the complete root and nested findings collected before failure.

## Optional parser logging

Logging is disabled by default. Use Python's logging-backed console or file
mode when operational diagnostics must be emitted:

```python
from EMLMailReader import LoggingMode, MailReader

console_reader = MailReader(logging_mode=LoggingMode.CONSOLE)
file_reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder="/existing/log/directory",
)
```

The target directory must already exist for file logging. Logger configuration
is process-wide, so applications should configure it deliberately rather than
construct competing readers with different destinations.

Avoid logging message bodies, raw source, authentication tokens, or complete
address lists unless the application's privacy policy explicitly permits it.
