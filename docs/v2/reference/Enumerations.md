# Enumerations

EMLMailReader exposes enums for transfer encodings, parser policy, syntax
classification, diagnostic severity, and logging.

## Imports

```python
from EMLMailReader import (
    DiagnosticSeverity,
    LoggingMode,
    ParsingMode,
    SyntaxStatus,
    TransferEncoding,
)
from EMLMailReader.Enumerations import LoggingLevel
```

`LoggingLevel` is used by the low-level `Logger.logentry()` API and is not
re-exported from the package root.

## TransferEncoding

String enum used by `TransferEncodingValue.kind`.

| Member | Value |
| --- | --- |
| `BASE64` | `"base64"` |
| `SEVEN_BIT` | `"7bit"` |
| `EIGHT_BIT` | `"8bit"` |
| `QUOTED_PRINTABLE` | `"quoted-printable"` |
| `BINARY` | `"binary"` |
| `UNKNOWN` | `"unknown"` |

Unknown wire tokens are represented by `UNKNOWN` while the original lowercase
token remains available in `TransferEncodingValue.raw_value`.

## LoggingMode

| Member | Numeric value | Behavior |
| --- | ---: | --- |
| `CONSOLE` | 1 | Configure root logging to the console |
| `FILE` | 2 | Configure root logging to a timestamped file |
| `NONE` | 3 | Do not configure logging |

```python
reader = MailReader(logging_mode=LoggingMode.CONSOLE)
```

## LoggingLevel

| Member | Numeric value |
| --- | ---: |
| `DEBUG` | 1 |
| `INFO` | 2 |
| `ERROR` | 3 |
| `CRITICAL` | 4 |

`Logger.logentry()` routes unknown levels through `logging.debug()`.

## ParsingMode

String enum accepted by `MailReader`:

| Member | Value |
| --- | --- |
| `MODERN` | `"modern"` |
| `LENIENT` | `"lenient"` |
| `STRICT` | `"strict"` |

See [Structured types](StructuredTypes.md) for mode behavior.

## SyntaxStatus

String enum stored in `HeaderField.syntax_status`:

| Member | Value |
| --- | --- |
| `CURRENT` | `"current"` |
| `OBSOLETE` | `"obsolete"` |
| `NONCONFORMANT` | `"nonconformant"` |

## DiagnosticSeverity

String enum stored in `ParseDiagnostic.severity`:

| Member | Value |
| --- | --- |
| `INFO` | `"info"` |
| `WARNING` | `"warning"` |
| `ERROR` | `"error"` |

## Removed legacy enums

The current API does not expose `EntityType` or `DispositionType`.
`ContentDisposition.DispositionType` is a string so registered and extension
tokens can both be retained.

## Related pages

- [Structured types](StructuredTypes.md)
- [Logger](Logger.md)
- [ContentDisposition](ContentDisposition.md)
