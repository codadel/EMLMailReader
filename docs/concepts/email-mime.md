# Email and MIME essentials

You do not need to understand every email standard to use EMLMailReader, but a
few terms explain why a parsed message can contain more than one body-like
section.

## EML file

An EML file is a stored email message. It normally contains:

1. headers such as From, To, Subject, and Date;
2. a blank line separating headers from content; and
3. a body, which may itself contain multiple MIME parts.

## MIME parts

MIME lets an email contain different types of content. A multipart message
might include:

- a plain-text body;
- an HTML body;
- an inline image; and
- file attachments.

In v1, the top-level message exposes child MIME entities through `Children`.
Each child is another `RxMailMessage` with its own `ContentType`, body, and
entity classification.

## Content type

`ContentType` describes what a part contains:

```text
text/plain; charset=utf-8
image/png; name=chart.png
multipart/mixed; boundary=example-boundary
```

The v1 object exposes `MediaType`, `Charset`, `Boundary`, and `Name`.

## Content disposition

`ContentDisposition` describes how content should be presented, such as inline
or as an attachment. It can also provide a filename, creation date,
modification date, and size.

## Transfer encoding

Email transports were historically designed around text. MIME transfer
encodings represent other content safely:

- **Base64** commonly represents binary attachments and non-ASCII text.
- **Quoted-Printable** represents mostly readable text with escaped bytes.
- **7bit** and **8bit** content is stored more directly.

EMLMailReader decodes these representations while parsing. Attachment contents
are exposed as bytes and body content as a string.

## Encoded headers

Subjects and display names can use encoded-word syntax such as
`=?utf-8?B?...?=`. v1 decodes common Base64 and Quoted-Printable encoded words.

Real-world email syntax has many edge cases. Review
[v1 behavior and limitations](v1-behavior.md) before treating parsed values as
fully validated standards data.
