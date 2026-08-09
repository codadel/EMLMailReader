# Understand the v2 message model

Every parsed result is an `RxMailMessage`. The root represents the complete
Internet message; every child represents another MIME entity using the same
class.

```text
RxMailMessage (root)
├── headers and Internet-message fields
├── content type and transfer encoding
├── raw and decoded bodies
├── diagnostics
└── Children
    ├── RxMailMessage (text/plain)
    ├── RxMailMessage (text/html)
    └── RxMailMessage (attachment)
```

## Internet-message fields

Common fields have structured projections while all header occurrences remain
available through `Headers`:

```python
print(message.Subject)
print(message.Date.raw_value if message.Date else None)
print(message.Date.value if message.Date else None)
print(message.MessageID.value if message.MessageID else None)

for mailbox in message.From.Mailboxes:
    print(mailbox.DisplayName, mailbox.Email)

for field in message.Headers:
    print(field.index, field.raw_name, field.decoded_value)
```

`Headers` preserves duplicates and source order. `get()` returns the last
matching value, while `get_all()` and `occurrences()` retain every match.

## Bodies and raw data

Each MIME node exposes several views:

| Property | Meaning |
| --- | --- |
| `RawSource` | Complete source bytes for the entity |
| `RawBody` | Body bytes before transfer decoding |
| `DecodedBody` | Transfer-decoded bytes for a leaf |
| `Body` | Preferred decoded text for the subtree |
| `TextBody` | First `text/plain` body in the subtree |
| `HtmlBody` | First `text/html` body in the subtree |

For `multipart/alternative`, `Body` selects the last non-empty alternative.
For other multipart containers it selects the first non-empty child body.

## Attachments are MIME nodes

`Attachments` and `InlineResources` are recursive tuple views over the same
nodes already present in `Children`:

```python
for attachment in message.Attachments:
    print(
        attachment.Name,
        attachment.ContentType.MediaType,
        len(attachment.DecodedBody),
    )
```

There are no parallel attachment objects to synchronize with the MIME tree.

## Serialization

```python
record = message.to_dict()
json_text = message.export_as_json()

assert record["schema_version"] == 2
```

The schema includes headers, addresses, dates, identifiers, MIME metadata,
bodies, children, and diagnostics. Raw byte payloads are intentionally omitted.
