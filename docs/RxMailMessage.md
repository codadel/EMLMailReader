# RxMailMessage

`RxMailMessage` represents both the root Internet message and every MIME entity
inside it. `Children` forms the MIME tree. Attachments and inline resources are
views over those same nodes.

Applications normally receive this class from `MailReader`; constructing it
directly creates an empty message model.

## Internet message fields

| Property | Type | Description |
| --- | --- | --- |
| `Headers` | `HeaderCollection` | Ordered, duplicate-preserving header occurrences |
| `From` | `AddressList` | Originator mailbox/group list |
| `Sender` | `AddressList` | Sender mailbox/group list |
| `ReplyTo` | `AddressList` | Reply-To mailbox/group list |
| `To` | `AddressList` | Primary recipients |
| `Cc` | `AddressList` | Carbon-copy recipients |
| `Bcc` | `AddressList` | Blind-copy recipients when present in the source |
| `Subject` | `str` | Decoded subject value, or an empty string |
| `Date` | `ParsedDateTime \| None` | Raw and parsed date metadata |
| `MessageID` | `ParsedMessageID \| None` | Structured Message-ID |
| `InReplyTo` | `list[ParsedMessageID]` | Parsed identifiers from In-Reply-To |
| `References` | `list[ParsedMessageID]` | Parsed identifiers from References |
| `Comments` | `list[str]` | All Comments header values |
| `Keywords` | `list[str]` | All Keywords header values |
| `Received` | `list[str]` | Unfolded Received values in source order |
| `ReturnPath` | `str` | Unfolded Return-Path value |
| `ResentBlocks` | `list[ResentBlock]` | Ordered groups of Resent fields |
| `TraceBlocks` | `list[TraceBlock]` | Grouped Return-Path and Received fields |

```python
message = MailReader().parse_bytes(source)

for mailbox in message.From.Mailboxes:
    print(mailbox.DisplayName, mailbox.Email)

for received in message.Headers.get_all("Received", decoded=False):
    print(received)
```

## MIME fields and source data

| Property | Type | Description |
| --- | --- | --- |
| `ContentType` | `ContentType` | Effective media type plus explicit header metadata |
| `ContentDisposition` | `ContentDisposition \| None` | Parsed disposition when the header exists |
| `ContentTransferEncoding` | `TransferEncodingValue` | Known or extension transfer-encoding token |
| `MimeVersion` | `str` | MIME-Version header value |
| `ContentDescription` | `str` | Decoded Content-Description |
| `ContentID` | `ParsedMessageID \| None` | Structured Content-ID |
| `MessagePartial` | `MessagePartialInfo \| None` | `message/partial` parameters |
| `ExternalBodyAccess` | `ExternalBodyAccessInfo \| None` | `message/external-body` parameters |
| `RawSource` | `bytes` | Header and body bytes for this node |
| `RawBody` | `bytes` | Body bytes before transfer decoding |
| `DecodedBody` | `bytes` | Transfer-decoded payload for a leaf node |
| `Children` | `list[RxMailMessage]` | Direct child MIME entities |
| `Preamble` | `str` | Multipart preamble |
| `Epilogue` | `str` | Multipart epilogue |
| `Diagnostics` | `list[ParseDiagnostic]` | Findings attached to this node |

For child nodes produced by Python's MIME parser, `RawSource` is a normalized
serialization of that child. The root `RawSource` is the exact byte sequence
supplied to `parse_bytes()` or read by `get_email()`.

## Computed properties

### `IsMultiPart`

True when the node has children or its media type starts with `multipart/`.

### `Body`

- A leaf returns its decoded text, or an empty string for a non-text leaf.
- `multipart/alternative` returns the last non-empty child body.
- Other containers return the first non-empty child body.

### `TextBody` and `HtmlBody`

These recursively return the first non-empty `text/plain` and `text/html`
values, respectively.

### `Name`

Uses `ContentDisposition.FileName` first, then `ContentType.Name`.

### `IsAttachment` and `IsInline`

`IsInline` is true for an explicit `inline` disposition. `IsAttachment` is true
for an explicit `attachment` disposition or a named part that is not inline.

### `Attachments` and `InlineResources`

Recursive tuple views containing matching `RxMailMessage` nodes.

```python
for attachment in message.Attachments:
    print(
        attachment.Name,
        attachment.ContentType.MediaType,
        len(attachment.DecodedBody),
    )

for resource in message.InlineResources:
    content_id = resource.ContentID.value if resource.ContentID else None
    print(content_id, resource.Name)
```

## MIME traversal

```python
def walk(part):
    yield part
    for child in part.Children:
        yield from walk(child)

for part in walk(message):
    print(part.ContentType.MediaType)
```

## Serialization

```python
data = message.to_dict()
json_text = message.export_as_json()

assert data["schema_version"] == 2
```

Both methods emit the one canonical recursive schema. `export_as_json()` uses
`ensure_ascii=False`. Raw and decoded byte payloads are not included in the
JSON-compatible dictionary. Attachment and inline views are also not repeated;
their parts already appear under `children`.

## Saving attachments

```python
message.save_attachments("/existing/output/directory")
```

- The directory must already exist or `FolderNotAvailableError` is raised.
- A supplied path is reduced to its basename.
- An empty, `.` or `..` name becomes `attachment`.
- `DecodedBody` is written for normal attachment leaves.
- Existing files with the same name are overwritten.
- Multiple attachments with the same name target the same output file.

## Related pages

- [MailReader](MailReader.md)
- [AddressList](AddressList.md)
- [ContentType](ContentType.md)
- [ContentDisposition](ContentDisposition.md)
- [Structured types](StructuredTypes.md)
