# Work with attachments

Attachments are available through `message.Attachments`. Each
`MailAttachment` contains metadata and decoded binary content.

## Inspect attachments

```python
for attachment in message.Attachments.export_as_list():
    print(f"Name: {attachment.Name}")
    print(f"Media type: {attachment.ContentType.MediaType}")
    print(f"Content ID: {attachment.ContentID}")
    print(f"Bytes: {len(attachment.Contents)}")
```

`Contents` is a `bytes` value held in memory. `ContentType` and
`ContentDisposition` expose the parsed MIME metadata.

## Convenience method for trusted messages

`save_attachments()` writes every attachment to an existing directory:

```python
from pathlib import Path

output_dir = Path("attachments")
output_dir.mkdir(parents=True, exist_ok=True)
message.save_attachments(str(output_dir))
```

!!! warning "Existing files are overwritten"

    v1 joins the message-supplied attachment name directly to the output
    directory and opens the destination in write mode. Use this convenience
    method only when attachment names come from a trusted source.

## Safer extraction for untrusted mail

Validate or replace message-supplied filenames and decide how to handle
collisions explicitly:

```python
from pathlib import Path


def safe_attachment_name(value, fallback):
    normalized = value.replace("\\", "/")
    name = Path(normalized).name
    return name if name not in {"", ".", ".."} else fallback


output_dir = Path("attachments")
output_dir.mkdir(parents=True, exist_ok=True)

for index, attachment in enumerate(
    message.Attachments.export_as_list(),
    start=1,
):
    name = safe_attachment_name(attachment.Name, f"attachment-{index}")
    destination = output_dir / name

    if destination.exists():
        raise FileExistsError(destination)

    destination.write_bytes(attachment.Contents)
```

Application-level policies may also need maximum attachment sizes, allowed
media types, malware scanning, and storage quotas.

## What v1 recognizes

The automatic extraction path primarily treats Base64-encoded `application/*`
and `image/*` MIME parts as attachments. Mail that represents attachments using
other media types or structures may require inspection through `Children` or a
more complete parser.
