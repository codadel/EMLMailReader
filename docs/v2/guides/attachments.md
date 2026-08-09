# Work with attachments and inline resources

Attachments are `RxMailMessage` nodes selected recursively from the MIME tree.

```python
for part in message.Attachments:
    print(part.Name)
    print(part.ContentType.MediaType)
    print(part.ContentDisposition.DispositionType if part.ContentDisposition else None)
    print(len(part.DecodedBody))
```

An explicit `attachment` disposition qualifies. A named MIME entity also
qualifies unless it is explicitly inline.

## Inline resources

```python
for part in message.InlineResources:
    content_id = part.ContentID.value if part.ContentID else None
    print(content_id, part.Name, part.ContentType.MediaType)
```

Inline resources remain in `Children`; the tuple is only a recursive view.

## Save decoded attachments

```python
from pathlib import Path

target = Path("/data/extracted/example")
target.mkdir(parents=True, exist_ok=True)
message.save_attachments(str(target))
```

The library requires the destination to exist, reduces filenames to their
basename, and overwrites collisions. If collision handling or content scanning
matters, iterate over `Attachments` and implement an application-specific save
policy instead.

Never trust a filename, media type, or extension solely because it appeared in
an email header.
