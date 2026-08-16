# Exceptions

The current public API exports three exception classes.

```python
from EMLMailReader import (
    FileMissingError,
    FolderNotAvailableError,
    StandardsComplianceError,
)
```

## StandardsComplianceError

```python
StandardsComplianceError(diagnostics)
```

Raised by `MailReader` in `ParsingMode.STRICT` when any root or nested parser
diagnostic has error severity.

The `diagnostics` attribute is an immutable tuple containing the complete
flattened diagnostic report, not only errors.

```python
from EMLMailReader import MailReader, ParsingMode, StandardsComplianceError

try:
    message = MailReader(parsing_mode=ParsingMode.STRICT).parse_bytes(source)
except StandardsComplianceError as error:
    for diagnostic in error.diagnostics:
        print(
            diagnostic.severity.value,
            diagnostic.code,
            diagnostic.message,
        )
```

The exception message lists the error diagnostic codes.

## FolderNotAvailableError

```python
FolderNotAvailableError(folderPath: str)
```

Raised when:

- `Logger.set_configuration(LoggingMode.FILE, ...)` receives a missing or empty
  target
- `RxMailMessage.save_attachments(...)` receives a path that is not an existing
  directory

The supplied path is available through `folderPath`.

```python
from EMLMailReader import FolderNotAvailableError

try:
    message.save_attachments("/missing/output")
except FolderNotAvailableError as error:
    print(error.folderPath)
```

## FileMissingError

```python
FileMissingError(filePath: str)
```

Carries the unavailable path in `filePath`. `MailReader.get_email()` uses this
exception internally but catches it with other filesystem read failures, logs
the error when configured, and returns `None`. Normal callers therefore check
the return value:

```python
message = MailReader().get_email("/missing/message.eml")
if message is None:
    print("Message was not available")
```

## Exceptions no longer present

The current package does not define the previous `InvalidEncodingError`,
`IncompleteHeaderError`, or `InvalidPropertyError` classes. Encoding and syntax
problems are represented by parser diagnostics or by the standard Python
exception raised by a direct utility call.

## Related pages

- [MailReader](MailReader.md)
- [RxMailMessage](RxMailMessage.md)
- [Logger](Logger.md)
- [Structured types](StructuredTypes.md)
