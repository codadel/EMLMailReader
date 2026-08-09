# v1 behavior and limitations

This page defines practical boundaries for EMLMailReader 1.0.4. It is especially
important when the input is untrusted or the output feeds analytics.

## Parsing and failures

- `get_email()` accepts a filesystem path, reads the whole file, and returns an
  `RxMailMessage` or `None`.
- It opens the EML file in text mode using the environment's default encoding.
- File and parse exceptions are caught internally and can be written to the
  configured logger.
- A partially malformed MIME entity can be logged and skipped while the parser
  still returns a message object.

Treat both a `None` result and unexpectedly empty fields as data-quality
signals.

## Memory and resource use

- v1 does not stream message content.
- Source lines, decoded bodies, attachment bytes, and MIME children can all be
  held in memory.
- v1 does not enforce message-size, part-count, nesting-depth, or attachment-size
  limits.

Check file size before parsing and process files sequentially when operating on
untrusted or large mail exports.

## Body selection

- `Body` is one convenience string.
- v1 does not expose separate plain-text and HTML body properties.
- Multipart processing can replace the top-level body with a non-empty child
  body.
- Use `Children` when you need to understand individual MIME alternatives.

## Attachment recognition and filenames

- Automatic extraction primarily recognizes Base64-encoded `application/*` and
  `image/*` parts.
- Other attachment encodings or media types may not appear in `Attachments`.
- `save_attachments()` uses the message-supplied filename and overwrites an
  existing destination with the same name.
- It does not sanitize path components in the supplied name.

Use application-level filename validation, collision handling, media-type
allowlists, and size limits for untrusted mail.

## Addresses and headers

- The address parser supports common `Name <address>` and bare-address forms.
- Recipient splitting is based on commas and semicolons; complex quoted mailbox
  syntax may not be preserved correctly.
- Header decoding supports common single encoded words but is not a complete
  implementation of every header-folding and encoded-word combination.
- Additional headers are stored in a dictionary. Repeated headers with the same
  name can overwrite an earlier value.

Do not use v1 address parsing as an email-address validator or as the basis for
an authorization decision.

## Dates and JSON

- `Date` remains the original header string; v1 does not normalize it to a
  `datetime`.
- `export_as_json()` returns a JSON string with selected metadata.
- The built-in JSON summary omits the body, MIME children, and attachment bytes.

Preserve raw values and perform normalization in your analytics layer.

## Logging

Logging uses Python's process-wide `logging.basicConfig()`. Existing application
logging configuration can affect whether new handlers are created.

## Choosing a parser

v1 works best for controlled collections that use common MIME structures. Use a
more standards-complete or resource-limited parser when you need adversarial
input handling, complete RFC fidelity, streaming, or security-sensitive
attachment processing.
