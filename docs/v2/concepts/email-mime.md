# Email and MIME essentials

An EML file combines two related formats:

- the Internet Message Format defines fields such as `From`, `Date`,
  `Message-ID`, and `Received`; and
- MIME defines media types, transfer encodings, multipart boundaries,
  attachments, and embedded messages.

## Headers are ordered fields

Headers are not a dictionary. A message can legally contain repeated fields,
field order can matter, and the source spelling may be useful during analysis.
`HeaderCollection` therefore stores one `HeaderField` per occurrence.

Each occurrence retains:

- its normalized and original name;
- folded source text and unfolded text;
- decoded Unicode text;
- its position and source line when known; and
- a current, obsolete, or nonconformant syntax classification.

## MIME is a tree

A multipart message is a recursive tree rather than one body plus a flat
attachment list. Nested alternatives, forwarded messages, and signed or
encrypted structures can contain several levels of child entities.

EMLMailReader represents every entity as `RxMailMessage`, so traversal code
does not need different cases for the root, a body part, or an attachment.

## Raw and interpreted values coexist

Analytics often needs normalized text, while investigations may need exact
source bytes. The model retains both whenever they answer different questions.
For example, `ParsedDateTime` keeps the raw field and a Python `datetime`, and
`TransferEncodingValue` keeps extension tokens instead of replacing them with
an assumed standard value.

## Diagnostics preserve recoverable mail

Real mail frequently contains obsolete or malformed syntax. Modern and lenient
modes return the recoverable message with diagnostics rather than discarding
all data. Strict mode is available when conformance is a hard requirement.
