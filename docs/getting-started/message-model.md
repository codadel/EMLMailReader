# Understand the message model

`MailReader.get_email()` returns an `RxMailMessage`. The object represents the
top-level email and, for multipart messages, contains child `RxMailMessage`
objects for individual MIME entities.

## Common fields

| Property | v1 value |
| --- | --- |
| `From` | `MailAddress` or `None` |
| `To`, `Cc`, `Bcc`, `ReplyTo` | `MailAddressCollection` |
| `Subject` | Decoded string |
| `Date` | Original header value as a string |
| `Body` | One decoded body string |
| `Headers` | Dictionary of headers not mapped to dedicated properties |
| `MessageID` | Original Message-ID value |
| `ContentType` | `ContentType` or `None` before parsing sets it |
| `IsMultiPart` | Boolean multipart indicator |
| `Children` | List of child `RxMailMessage` MIME entities |
| `Attachments` | Flattened `MailAttachmentCollection` |

## Addresses

```python
if message.From is not None:
    print(message.From.DisplayName)
    print(message.From.Email)

for address in message.Cc.export_as_list():
    print(address.DisplayName, address.Email)
```

Calling `str()` on an address produces `Name <address>` when a display name is
available. Calling `str()` on a recipient collection joins addresses with
semicolons.

## Multipart messages

For a multipart email, `Children` preserves the MIME entity hierarchy while
`Attachments` collects attachments discovered in child parts.

```python
print(message.IsMultiPart)

for child in message.Children:
    media_type = child.ContentType.MediaType if child.ContentType else None
    print(media_type, child.EntityType)
```

The top-level `Body` is a convenience string, not a collection of every body
alternative. v1 does not provide separate `text/plain` and `text/html` fields.
Inspect `Children` when MIME structure matters to your analysis.

## Collection snapshots

`export_as_list()` returns a deep copy of the collection. Modifying the returned
list or its objects does not update the collection stored on the message.

```python
attachments = message.Attachments.export_as_list()
recipients = message.To.export_as_list()
```

## JSON summary

`message.export_as_json()` returns a JSON string containing selected metadata.
It intentionally excludes `Body`, `Children`, and attachment bytes. See
[Export parsed data](../guides/exporting.md) for the exact schema and an
analytics-oriented alternative.
