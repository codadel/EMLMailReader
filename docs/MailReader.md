# MailReader

`MailReader` is the public parsing façade. It supports filesystem, bytes,
string, and stream inputs and returns an `RxMailMessage` tree.

## Constructor

```python
MailReader(
    logging_mode=LoggingMode.NONE,
    TargetLoggingFolder="",
    parsing_mode=ParsingMode.MODERN,
    limits=None,
)
```

| Parameter | Type | Behavior |
| --- | --- | --- |
| `logging_mode` | `LoggingMode` | `NONE`, `CONSOLE`, or `FILE` |
| `TargetLoggingFolder` | `str` | Existing output directory required for file logging |
| `parsing_mode` | `ParsingMode \| str` | `modern`, `lenient`, or `strict`; unknown strings fall back to modern |
| `limits` | `ParserLimits \| None` | Parser resource limits; defaults to `ParserLimits()` |

The instance exposes `ParsingMode` and `LoggingMode` with the values supplied
to the constructor.

```python
from EMLMailReader import LoggingMode, MailReader, ParserLimits, ParsingMode

reader = MailReader(
    logging_mode=LoggingMode.CONSOLE,
    parsing_mode=ParsingMode.MODERN,
    limits=ParserLimits(max_message_bytes=25 * 1024 * 1024),
)
```

## `get_email()`

```python
get_email(emlPath: str) -> RxMailMessage | None
```

Reads an EML file as bytes and delegates to `parse_bytes()`.

- Returns an `RxMailMessage` when parsing succeeds.
- Returns `None` when the path is missing, the file is empty, or a filesystem
  read fails.
- Logs filesystem errors when logging is configured.
- Propagates `StandardsComplianceError` in strict mode.
- Closes the source file on success and failure.

```python
message = MailReader().get_email("message.eml")
if message is None:
    print("Message could not be read")
```

`FileMissingError` is used internally but is caught by `get_email()`; callers
normally detect this case from the `None` result.

## `parse_bytes()`

```python
parse_bytes(source: bytes) -> RxMailMessage
```

This is the preferred in-memory entry point because the parser can retain the
exact source octets in `RawSource`.

```python
source = (
    b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
    b"From: Alice <alice@example.com>\r\n"
    b"Subject: Hello\r\n\r\n"
    b"Body"
)
message = MailReader().parse_bytes(source)

assert message.RawSource == source
assert message.Subject == "Hello"
```

After parsing, diagnostics from the root and nested MIME parts are forwarded to
the configured logger. The diagnostics remain attached to their message nodes.

## `parse_string()`

```python
parse_string(source: str, encoding: str = "utf-8") -> RxMailMessage
```

Encodes the string with the requested encoding, then calls `parse_bytes()`.
Because this creates new bytes, use `parse_bytes()` when exact original wire
bytes are available.

```python
message = MailReader().parse_string(
    "Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
    "From: alice@example.com\r\n\r\nHello"
)
```

## `parse_stream()`

```python
parse_stream(stream) -> RxMailMessage
```

Reads from the stream's current position. Binary stream data is passed through;
text stream data is encoded as UTF-8.

```python
from io import BytesIO, StringIO

reader = MailReader()
binary_message = reader.parse_stream(BytesIO(source))
text_message = reader.parse_stream(StringIO(source.decode("ascii")))
```

The caller owns the stream; `parse_stream()` does not close it.

## Parsing modes

```python
from EMLMailReader import (
    MailReader,
    ParsingMode,
    StandardsComplianceError,
)

try:
    message = MailReader(
        parsing_mode=ParsingMode.STRICT
    ).parse_bytes(source)
except StandardsComplianceError as error:
    for diagnostic in error.diagnostics:
        print(diagnostic.code)
```

- `MODERN` returns the parsed tree and diagnostics.
- `LENIENT` is an explicit receiver-policy label and also returns the parsed
  tree and diagnostics.
- `STRICT` raises when any root or nested diagnostic has error severity.

See [Structured types](StructuredTypes.md) for `ParserLimits`,
`ParseDiagnostic`, and `StandardsComplianceError`.

## Logging

```python
from EMLMailReader import LoggingMode, MailReader

console_reader = MailReader(logging_mode=LoggingMode.CONSOLE)
file_reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder="/existing/log/directory",
)
```

File mode validates the target during construction and may raise
`FolderNotAvailableError`. Configuring console or file logging replaces the
process root logger configuration; see [Logger](Logger.md).

## Related pages

- [RxMailMessage](RxMailMessage.md)
- [Structured types](StructuredTypes.md)
- [Logger](Logger.md)
- [Exceptions](Exceptions.md)
