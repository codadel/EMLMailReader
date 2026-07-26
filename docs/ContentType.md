# ContentType

`ContentType` stores the effective MIME media type and all decoded parameters
for one `RxMailMessage` node.

## Default state

```python
from EMLMailReader import ContentType

content_type = ContentType()
```

| Property | Default | Description |
| --- | --- | --- |
| `MediaType` | `"text/plain"` | Lowercase type and subtype |
| `Charset` | `"us-ascii"` | Text charset or MIME default |
| `Boundary` | `""` | Multipart boundary |
| `Name` | `""` | Decoded `name` parameter |
| `Parameters` | `{}` | All decoded, lowercase-keyed parameters |
| `RawValue` | `""` | Original header value passed to `parse()` |
| `IsExplicit` | `False` | Whether a Content-Type header value was supplied |

## Parsing

```python
parse(
    ContentTypeString: str | None = None,
    *,
    effective_media_type: str | None = None,
) -> None
```

```python
content_type.parse('multipart/mixed; boundary="part-boundary"; name="message.eml"')

assert content_type.MediaType == "multipart/mixed"
assert content_type.Boundary == "part-boundary"
assert content_type.Name == "message.eml"
assert content_type.IsExplicit
```

MIME parameters, including decoded extended parameters handled by Python's
email package, are exposed in `Parameters`.

When no explicit value is supplied, `effective_media_type` can provide the
parser's context-sensitive default. Otherwise the default is `text/plain`.
`RawValue` remains empty and `IsExplicit` remains false for an effective
default.

## Parameter lookup

```python
format_value = content_type.get_parameter("FORMAT", default=None)
```

Parameter names are case-insensitive because lookup lowercases the requested
name.

## Header and dictionary forms

```python
header_value = content_type.to_header_value()
same_value = str(content_type)
data = content_type.to_dict()
```

`to_dict()` returns:

```python
{
    "media_type": "multipart/mixed",
    "charset": "us-ascii",
    "boundary": "part-boundary",
    "name": "message.eml",
    "parameters": {
        "boundary": "part-boundary",
        "name": "message.eml",
    },
    "raw_value": 'multipart/mixed; boundary="part-boundary"; name="message.eml"',
    "is_explicit": True,
}
```

## Related pages

- [RxMailMessage](RxMailMessage.md)
- [ContentDisposition](ContentDisposition.md)
