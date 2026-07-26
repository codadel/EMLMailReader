# TextEncoding

`TextEncoding` provides four static decoding helpers. Parsed messages already
use these decoding behaviors where appropriate; call the helpers directly when
working with standalone encoded values.

## `decode_header()`

```python
TextEncoding.decode_header(
    encoded_string: str | None,
    errors: str = "replace",
) -> str
```

Decodes and joins RFC 2047 encoded-word fragments.

```python
from EMLMailReader import TextEncoding

subject = TextEncoding.decode_header(
    "=?utf-8?b?SGVsbG8g4pyT?="
)
assert subject == "Hello ✓"
assert TextEncoding.decode_header(None) == ""
```

Byte fragments use their declared charset, or ASCII when no charset is
provided. The `errors` argument is passed to `bytes.decode()`.

## `decode_base64_string()`

```python
TextEncoding.decode_base64_string(
    encoded_string: str,
    string_charset: str = "utf-8",
) -> str
```

```python
text = TextEncoding.decode_base64_string("SGVsbG8=")
assert text == "Hello"
```

The method Base64-decodes the input and then decodes the resulting bytes with
`string_charset`.

## `decode_base64_file()`

```python
TextEncoding.decode_base64_file(file_contents: str) -> bytes
```

Despite its historical name, this method performs no file I/O. It accepts a
Base64 string and returns decoded bytes.

```python
payload = TextEncoding.decode_base64_file("AAEC")
assert payload == b"\x00\x01\x02"
```

## `decode_quoted_printable_string()`

```python
TextEncoding.decode_quoted_printable_string(
    encoded_string: str,
    string_charset: str,
    is_header: bool,
) -> str
```

```python
text = TextEncoding.decode_quoted_printable_string(
    "caf=C3=A9",
    "utf-8",
    False,
)
assert text == "café"
```

An empty charset is treated as UTF-8. `is_header=True` enables quoted-printable
header rules, including underscore-to-space conversion.

## Error behavior

These are low-level helpers. Invalid Base64 data, unknown charsets, or
undecodable bytes can raise standard Python decoding exceptions. They do not
produce `ParseDiagnostic` objects when called directly.

During normal message parsing, body charset failures are recovered with UTF-8
replacement decoding and a diagnostic is stored on the affected MIME node.

## Related pages

- [MailReader](MailReader.md)
- [RxMailMessage](RxMailMessage.md)
- [Structured types](StructuredTypes.md)
