# API reference

This reference is generated from the v1.0.4 source docstrings. It describes the
public classes exported by the `EMLMailReader` package.

## Main entry points

- [`MailReader`](core.md) parses an EML path.
- [`RxMailMessage`](core.md) contains the parsed result.
- [`MailAddress` and `MailAddressCollection`](addresses.md) represent mailbox
  values.
- [`MailAttachment` and `MailAttachmentCollection`](attachments.md) represent
  decoded attachment data.

## Supporting types

- [MIME types and enumerations](mime.md) describe parsed MIME metadata.
- [Utilities and exceptions](utilities.md) document exported helpers and error
  types.

Methods whose docstrings say **internal use only** support the parser's own
construction process. Application code should normally use `MailReader`, read
the resulting properties, and call `export_as_json()` or `save_attachments()`.
