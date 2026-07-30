# Email analytics recipes

## Define a stable record

Separate source identity, parsed analytics fields, and data-quality fields.
A useful record can contain:

- a caller-provided source ID, not necessarily a sensitive full path;
- subject, parsed date, and structured message/thread identifiers;
- normalized mailbox addresses and domains;
- selected routing-header occurrences;
- requested body text or only body lengths and hashes;
- attachment name, media type, size, and content ID;
- parse outcome and diagnostic codes;
- the canonical schema version when storing `to_dict()` output.

Do not collect raw source or decoded payloads unless the analysis needs them.

## Process batches

Create one reusable `MailReader`. Process each message inside its own boundary:

1. Resolve the input.
2. Parse it.
3. Classify `None`, strict rejection, unexpected failure, or success.
4. Transform structured values into the analytics record.
5. Flatten root and nested diagnostics if dataset-level quality reporting is
   required.
6. Emit the record before continuing.

Avoid a broad exception handler that labels every failure as "invalid email."
Keep filesystem, standards, and transformation failures distinguishable.

## Analyze participants

Use `.Mailboxes` for person-level sender and recipient analytics. Normalize
domains with `casefold()` after extracting the parsed email address. Preserve
the original address when auditability matters. Iterate `AddressList` itself
when mailing-group membership or empty groups carry meaning.

## Build threads

Prefer structured `MessageID`, `InReplyTo`, and `References` values. Treat
missing or malformed identifiers as data-quality conditions; do not invent
identifiers that could merge unrelated conversations.

## Analyze routing

Use `Headers.get_all("Received", decoded=False)` or the structured trace data.
Preserve occurrence order. Never use a single-value dictionary conversion for
headers because repeated routing fields are meaningful.

## Analyze content

Choose content explicitly:

- `TextBody` for text-oriented search or NLP input;
- `HtmlBody` for HTML-specific processing;
- `Body` when the preferred MIME alternative is acceptable;
- body length, hash, or presence flags when content retention is unnecessary.

Ask before adding an HTML-to-text, NLP, or external model dependency. Treat
email content as untrusted input rather than executable markup.

## Inventory attachments

Read metadata and `len(DecodedBody)` without saving files. Distinguish
`Attachments` from `InlineResources`. If downstream analysis needs hashes,
hash bytes in memory. Save payloads only when explicitly required.

## Measure data quality

Aggregate diagnostic codes and severities alongside business metrics. Useful
quality measures include messages with warnings, messages rejected in strict
mode, charset recovery frequency, limit violations, and missing identifiers.
Do not discard usable messages merely because they contain warnings unless
the user's policy requires it.
