# Library implementation

This document gives maintainers and AI agents the implementation context needed
to change EMLMailReader safely. Public usage belongs in `README.md` and
`docs/`; test and release procedures live in their dedicated `ai-docs` files.

## Purpose and standards

EMLMailReader is a dependency-free Python library that parses EML files and
in-memory Internet messages into a structured `RxMailMessage` and MIME tree.
It is a receiver-oriented parser: recoverable input is retained, raw and
interpreted values are exposed, and standards defects are recorded as
diagnostics.

The implemented standards bundle covers:

- RFC 5322 Internet Message Format
- RFC 6854 updated originator and destination syntax
- MIME, including RFC 2045 through RFC 2049
- RFC 2183 Content-Disposition
- RFC 2231 parameter continuations and character sets
- RFC 6532 internationalized headers

Do not describe receiver-mode acceptance of obsolete or malformed mail as
perfect source conformance. Modern and lenient parsing may return a message
with diagnostics; strict parsing is the conformance-enforcement path.

## Source map

- `EMLMailReader/Mail_Reader.py` is the public parsing facade for file, byte,
  string, and stream input. It also forwards parser diagnostics to logging.
- `EMLMailReader/RFC_Parser.py` contains parsing, validation, MIME traversal,
  transfer and charset decoding, diagnostics, and resource-limit enforcement.
- `EMLMailReader/Rx_Mail_Message.py` defines the canonical root/MIME-node
  model, body and attachment views, serialization, and attachment saving.
- `EMLMailReader/Standards.py` defines parser modes, limits, diagnostics,
  ordered headers, structured dates and identifiers, resent and trace blocks,
  transfer-encoding values, and message-specific MIME metadata.
- `EMLMailReader/Mail_Address.py` defines `MailAddress`, `AddressList`, and
  address-group behavior.
- `EMLMailReader/Content_Type.py` and
  `EMLMailReader/Content_Disposition.py` parse MIME field values and parameters.
- `EMLMailReader/Text_Encoding.py` decodes encoded header text.
- `EMLMailReader/Processing_Logs.py` integrates with Python logging.
- `EMLMailReader/Enumerations.py` and
  `EMLMailReader/Custom_Exceptions.py` contain shared public values.
- `EMLMailReader/__init__.py` defines package-root public imports.
- `EMLMailReader/py.typed` marks the installed package as providing inline
  annotations to PEP 561-aware type checkers.

The project requires Python 3.12 or newer. Runtime code uses only the Python
standard library. Development dependencies are in `requirements.txt`, and
package metadata is in `pyproject.toml`. Strict typing, formatting, linting,
and check-only automation are documented in [Code quality](QUALITY.md).

## Canonical public model

This major version deliberately has one model. Do not add parallel legacy and
modern properties or compatibility projections.

- `RxMailMessage` represents both the root message and every MIME entity.
- `Children` owns the MIME tree.
- `Attachments` and `InlineResources` are recursive immutable tuple views over
  `RxMailMessage` nodes already in the tree.
- There are no separate attachment, attachment-collection, or
  address-collection classes.
- `From`, `Sender`, `ReplyTo`, `To`, `Cc`, and `Bcc` are `AddressList`
  properties. `.Mailboxes` is the flattened immutable mailbox view; iterating
  the list retains group boundaries.
- `Headers` is an ordered, duplicate-preserving `HeaderCollection` with
  case-insensitive lookup.
- `HeaderField` retains raw, unfolded, decoded, source-position, and syntax
  status values.
- `Date`, `MessageID`, `InReplyTo`, `References`, and `ContentID` use
  structured values rather than parallel raw and parsed properties.
- `Body`, `TextBody`, and `HtmlBody` are computed from the MIME tree.
- `RawSource`, `RawBody`, and `DecodedBody` are byte-oriented. Root
  `RawSource` preserves the exact input supplied to `parse_bytes()`.
- `to_dict()` and `export_as_json()` emit the sole recursive schema with
  `schema_version` set to `2`.
- Raw byte payloads are not serialized. Attachments and inline resources are
  not duplicated because their nodes already appear under `children`.

Removed names such as `HeaderFields`, `FromAddresses`, `SenderAddress`,
`ReplyToAddresses`, `ToAddresses`, `EffectiveContentType`, `PreferredBody`,
and `compatibility_mode` must remain absent unless the user establishes a new
compatibility policy.

When changing the public surface, update `EMLMailReader/__init__.py`, the
relevant tests, and the corresponding `docs/` page. `LoggingLevel` is
intentionally imported from `EMLMailReader.Enumerations` rather than the
package root.

## Parsing entry points and error contracts

`MailReader` provides:

- `get_email(path)` for an EML file
- `parse_bytes(source)` for lossless in-memory bytes
- `parse_string(source, encoding="utf-8")` for text encoded before parsing
- `parse_stream(stream)` for a binary or text stream at its current position

Preserve these contracts:

- `get_email()` returns `None` for missing, empty, or unreadable files.
- Files opened by `get_email()` are closed on success and failure.
- Strict standards errors propagate as `StandardsComplianceError`; they are
  not converted to `None`.
- In-memory parsing methods do not hide input or compliance errors as
  filesystem failures.
- `parse_stream()` does not close the caller-owned stream.

## Modes and diagnostics

- `ParsingMode.MODERN` returns the parsed tree with diagnostics.
- `ParsingMode.LENIENT` is an explicit receiver-policy label and also returns
  the parsed tree with diagnostics.
- `ParsingMode.STRICT` raises `StandardsComplianceError` when a root or nested
  diagnostic has error severity.
- Diagnostics are stored on the MIME node where the issue occurred.
- Strict exceptions expose the flattened root and nested diagnostic set in
  their `diagnostics` tuple.
- Preserve diagnostic codes and RFC, section, header, line, and column
  metadata when changing validation.
- Accepted obsolete syntax should be marked obsolete rather than silently
  represented as current syntax.

## Resource and MIME invariants

`ParserLimits` guards message bytes, header bytes, header count, MIME depth,
MIME part count, and decoded-part bytes. Recursive parsing and decoding changes
must continue to enforce every limit. Violations produce error diagnostics and
cause strict mode to raise.

When changing MIME processing:

- Preserve raw header and body information before decoding.
- Keep content-transfer decoding separate from text charset decoding.
- Treat US-ASCII as the MIME default for text without an explicit charset and
  diagnose recoverable charset failures.
- Preserve extension or unknown transfer-encoding tokens through
  `TransferEncodingValue`.
- Retain multipart preamble and epilogue.
- Preserve nested `message/rfc822`, `message/partial`, and
  `message/external-body` behavior and metadata.
- Do not weaken attachment filename sanitization. The target directory must
  already exist, and supplied names must be reduced to a safe basename.

## Implementation change guidance

- Preserve the current public PascalCase property names unless a requested
  breaking change explicitly replaces them.
- Prefer focused parser helpers and structured types over parallel state on
  `RxMailMessage`.
- Add a diagnostic when receiver-mode recovery would otherwise hide a
  standards defect.
- Keep public data compatible with the canonical recursive serialization.
- For parser changes, test raw preservation, interpreted values, diagnostics,
  and strict behavior where applicable.
- Update public documentation only for implemented behavior. Planning notes,
  compliance gap analysis, and release checklists belong outside `docs/`.
