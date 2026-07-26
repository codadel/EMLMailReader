# Structured types

The parser exports typed values for headers, diagnostics, identifiers, dates,
resource limits, trace data, and MIME metadata. These types are available from
the package root.

## ParsingMode

```python
from EMLMailReader import ParsingMode
```

| Value | Behavior |
| --- | --- |
| `ParsingMode.MODERN` | Return the parsed tree with diagnostics |
| `ParsingMode.LENIENT` | Explicit receiver-policy label; return the parsed tree with diagnostics |
| `ParsingMode.STRICT` | Raise `StandardsComplianceError` when any error diagnostic exists |

## ParserLimits

`ParserLimits` is a frozen data class passed to `MailReader`.

```python
from EMLMailReader import MailReader, ParserLimits

limits = ParserLimits(
    max_message_bytes=25 * 1024 * 1024,
    max_header_bytes=512 * 1024,
    max_header_count=5_000,
    max_mime_depth=30,
    max_parts=2_000,
    max_decoded_part_bytes=10 * 1024 * 1024,
)
reader = MailReader(limits=limits)
```

| Field | Default |
| --- | ---: |
| `max_message_bytes` | 104,857,600 |
| `max_header_bytes` | 1,048,576 |
| `max_header_count` | 10,000 |
| `max_mime_depth` | 100 |
| `max_parts` | 10,000 |
| `max_decoded_part_bytes` | 104,857,600 |

Limit violations produce error diagnostics. Strict mode raises after collecting
the complete root and nested diagnostic set.

## Diagnostics

### ParseDiagnostic

```python
ParseDiagnostic(
    code: str,
    message: str,
    severity: DiagnosticSeverity = DiagnosticSeverity.WARNING,
    rfc: str | None = None,
    section: str | None = None,
    header: str | None = None,
    line: int | None = None,
    column: int | None = None,
)
```

`to_dict()` returns these fields and serializes severity as `"info"`,
`"warning"`, or `"error"`.

Diagnostics are stored on the affected `RxMailMessage.Diagnostics` list.
Strict-mode exceptions expose a flattened tuple through
`StandardsComplianceError.diagnostics`.

```python
from EMLMailReader import DiagnosticSeverity

errors = [
    item
    for item in message.Diagnostics
    if item.severity == DiagnosticSeverity.ERROR
]
```

### DiagnosticSeverity

- `INFO`
- `WARNING`
- `ERROR`

## HeaderCollection and HeaderField

`HeaderCollection` is an ordered `Sequence[HeaderField]`. It preserves
duplicates and performs case-insensitive lookup.

```python
subject = message.Headers.get("subject")
received = message.Headers.get_all("Received", decoded=False)
subject_occurrences = message.Headers.occurrences("Subject")
```

| Method | Result |
| --- | --- |
| `get(name, default=None, decoded=True)` | Last matching value or the default |
| `get_all(name, decoded=True)` | All matching values in source order |
| `occurrences(name)` | Matching `HeaderField` objects |
| `append(field)` | Add an occurrence |
| `to_list()` | Serialize every field |

With `decoded=True`, lookups use `HeaderField.decoded_value`. With
`decoded=False`, they use `unfolded_value`.

`HeaderField` is a frozen data class:

| Field | Type |
| --- | --- |
| `name` | `str` |
| `raw_name` | `str` |
| `raw_value` | `str` |
| `unfolded_value` | `str` |
| `decoded_value` | `str` |
| `index` | `int` |
| `line` | `int \| None` |
| `syntax_status` | `SyntaxStatus` |

`SyntaxStatus` values are `CURRENT`, `OBSOLETE`, and `NONCONFORMANT`.

## ParsedDateTime

```python
ParsedDateTime(
    raw_value: str,
    value: datetime | None,
    valid: bool,
    obsolete: bool = False,
)
```

`to_dict()` serializes `value` with `datetime.isoformat()`. Invalid values keep
their `raw_value`, set `value` to `None`, and set `valid` to false.

## ParsedMessageID

```python
ParsedMessageID(
    raw_value: str,
    value: str,
    left: str,
    right: str,
    valid: bool = True,
)
```

`raw_value` retains the original bracketed form. `value` is the identifier
without angle brackets. Invalid source values still retain their parsed pieces
with `valid=False`.

## TransferEncodingValue

```python
from EMLMailReader import TransferEncodingValue

encoding = TransferEncodingValue.parse("x-custom")
assert encoding.raw_value == "x-custom"
assert encoding.is_extension
```

| Field | Type | Description |
| --- | --- | --- |
| `raw_value` | `str` | Lowercase wire token |
| `kind` | `TransferEncoding` | Known enum value or `UNKNOWN` |
| `is_extension` | `bool` | True for an unrecognized/extension token |

`to_dict()` serializes `kind` using its string value.

## Message-specific MIME metadata

### MessagePartialInfo

Used by `message/partial` nodes:

```python
MessagePartialInfo(id: str, number: int | None, total: int | None)
```

### ExternalBodyAccessInfo

Used by `message/external-body` nodes:

```python
ExternalBodyAccessInfo(access_type: str, parameters: dict)
```

## Resent and trace blocks

### ResentBlock

Contains a `fields: HeaderCollection`. `to_dict()` returns the serialized list
of those header fields.

### TraceBlock

Contains:

- `return_path: str | None`
- `received: list[str]`

`to_dict()` returns both values without losing Received ordering.

## AddressGroup

Address groups are documented with [AddressList](AddressList.md).

## Related pages

- [MailReader](MailReader.md)
- [RxMailMessage](RxMailMessage.md)
- [Enumerations](Enumerations.md)
- [Exceptions](Exceptions.md)
