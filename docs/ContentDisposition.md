# ContentDisposition

`ContentDisposition` stores the disposition and decoded parameters from a
Content-Disposition header. `RxMailMessage.ContentDisposition` is `None` when
the header is absent.

## Properties

| Property | Type | Description |
| --- | --- | --- |
| `DispositionType` | `str` | Lowercase registered or extension token |
| `FileName` | `str` | Decoded filename parameter |
| `CreationDate` | `ParsedDateTime \| None` | Parsed `creation-date` parameter |
| `ModificationDate` | `ParsedDateTime \| None` | Parsed `modification-date` parameter |
| `ReadDate` | `ParsedDateTime \| None` | Parsed `read-date` parameter |
| `Size` | `int` | Numeric size parameter, or `0` when absent/invalid |
| `Parameters` | `dict[str, str]` | All decoded parameters with lowercase keys |
| `RawValue` | `str` | Header value supplied to `parse()` |
| `IsExplicit` | `bool` | True when a non-empty value was supplied |

## Parsing

```python
from EMLMailReader import ContentDisposition

disposition = ContentDisposition()
disposition.parse(
    'attachment; filename="report.pdf"; size=1200; '
    'creation-date="Fri, 21 Nov 1997 09:55:06 -0600"'
)

assert disposition.DispositionType == "attachment"
assert disposition.FileName == "report.pdf"
assert disposition.Size == 1200
assert disposition.CreationDate.valid
```

```python
parse(ContentDispositionString: str) -> None
```

Each call replaces the parsed state. Extension disposition tokens and
parameters are retained rather than rejected.

Date parameters produce `ParsedDateTime` even when invalid; inspect its
`valid` and `value` fields.

## Parameter lookup

```python
value = disposition.get_parameter("filename", default="")
```

Lookup is case-insensitive.

## Header and dictionary forms

```python
header_value = disposition.to_header_value()
same_value = str(disposition)
data = disposition.to_dict()
```

The dictionary contains:

```python
{
    "type": "attachment",
    "filename": "report.pdf",
    "creation_date": {
        "raw_value": "Fri, 21 Nov 1997 09:55:06 -0600",
        "value": "1997-11-21T09:55:06-06:00",
        "valid": True,
        "obsolete": False,
    },
    "modification_date": None,
    "read_date": None,
    "size": 1200,
    "parameters": {
        "filename": "report.pdf",
        "size": "1200",
        "creation-date": "Fri, 21 Nov 1997 09:55:06 -0600",
    },
    "raw_value": (
        'attachment; filename="report.pdf"; size=1200; '
        'creation-date="Fri, 21 Nov 1997 09:55:06 -0600"'
    ),
    "is_explicit": True,
}
```

## Attachment classification

`RxMailMessage.IsInline` checks for `DispositionType == "inline"`.
`RxMailMessage.IsAttachment` checks for `attachment`, or for a named part that
is not inline. The attachment itself remains an `RxMailMessage`.

## Related pages

- [RxMailMessage](RxMailMessage.md)
- [ContentType](ContentType.md)
- [Structured types](StructuredTypes.md)
