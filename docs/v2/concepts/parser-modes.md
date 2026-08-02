# Parsing modes, diagnostics, and limits

## Choose a parsing mode

```python
from EMLMailReader import MailReader, ParsingMode

modern = MailReader(parsing_mode=ParsingMode.MODERN)
lenient = MailReader(parsing_mode=ParsingMode.LENIENT)
strict = MailReader(parsing_mode=ParsingMode.STRICT)
```

| Mode | Result |
| --- | --- |
| `MODERN` | Returns recoverable mail and records standards findings |
| `LENIENT` | Receiver-oriented parsing with diagnostics for problematic input |
| `STRICT` | Raises when any error-level diagnostic is collected |

Modern and lenient currently share the receiver-oriented outcome. Keeping them
as distinct modes allows applications to state intent and permits their policy
to evolve independently.

## Inspect diagnostics recursively

```python
def diagnostics(message):
    yield from message.Diagnostics
    for child in message.Children:
        yield from diagnostics(child)


for item in diagnostics(message):
    print(item.code, item.severity.value, item.rfc, item.section)
```

Diagnostic codes are the stable value for grouping and automation. Human
messages may become more descriptive over time.

## Handle strict failures

```python
from EMLMailReader import StandardsComplianceError

try:
    message = strict.parse_bytes(source)
except StandardsComplianceError as error:
    for item in error.diagnostics:
        print(item.code, item.message)
```

The exception contains diagnostics from the root and all nested MIME parts.

## Apply resource limits

Email is untrusted input. Configure bounds appropriate for the dataset and
available memory:

```python
from EMLMailReader import MailReader, ParserLimits

reader = MailReader(
    limits=ParserLimits(
        max_message_bytes=25 * 1024 * 1024,
        max_header_bytes=512 * 1024,
        max_header_count=5_000,
        max_mime_depth=30,
        max_parts=2_000,
        max_decoded_part_bytes=10 * 1024 * 1024,
    )
)
```

Receiver modes attach limit diagnostics and return what could be recovered.
Strict mode raises when a limit produces an error-level diagnostic.
