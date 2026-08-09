---
name: use-emlmailreader
description: Build reliable, typed, and tested Python applications with EMLMailReader's canonical API. Use when an agent needs to parse EML files or in-memory messages, create email analytics or ingestion pipelines, extract participants, headers, bodies, MIME parts, or attachment metadata, handle malformed email and diagnostics, configure safe parser limits, write EMLMailReader tests, or migrate a v1.0.4 integration to the current major-version model.
---

# Use EMLMailReader

Build email parsing and analytics code around the library's structured values,
diagnostics, and recursive MIME model. Prefer complete, quality-aware records
over fragile string parsing or silent data loss.

## Prepare

1. Read the target repository's instructions and inspect its existing code,
   Python version, dependency policy, test framework, and installed
   EMLMailReader version.
2. Confirm that the requested API exists locally. The canonical API includes
   `MailReader.parse_bytes`, `ParsingMode`, `ParserLimits`,
   `RxMailMessage.Children`, and `RxMailMessage.Diagnostics`.
3. If those names are absent or legacy attachment/address classes are in use,
   read [migration-from-v1.md](references/migration-from-v1.md) before editing.
4. Ask for clarification only when the intended analytics output, acceptable
   data retention, or failure policy would materially change the design.

## Design the ingestion boundary

1. Collect only the fields required by the user's analysis. Do not retain raw
   source, bodies, or decoded attachments when metadata is sufficient.
2. Select the input method deliberately:
   - Use `get_email()` for filesystem paths.
   - Use `parse_bytes()` for exact source-byte preservation.
   - Use `parse_string()` for message text.
   - Use `parse_stream()` for caller-owned binary or text streams.
3. Treat one message as one failure boundary in batch jobs. Record a stable
   outcome for missing, unreadable, nonconformant, and successfully parsed
   messages; do not let one bad file terminate the batch unless requested.
4. Choose parsing policy explicitly:
   - Use `MODERN` for normal analytics ingestion with diagnostics.
   - Use `STRICT` when invalid messages must be rejected.
   - Use `LENIENT` only when the user wants that receiver-policy label.
5. Configure `ParserLimits` for untrusted or high-volume inputs. Derive limits
   from the workload instead of copying arbitrary maximums.

Read [api-patterns.md](references/api-patterns.md) for concrete API contracts
and [privacy-and-safety.md](references/privacy-and-safety.md) before processing
real, untrusted, or sensitive email.

## Implement with structured values

1. Use address objects and `.Mailboxes`; never split address headers with
   commas or regular expressions.
2. Use `Headers.get_all()` for repeated fields and `Headers.occurrences()` when
   raw, decoded, position, or syntax-status information matters.
3. Choose `TextBody`, `HtmlBody`, or `Body` according to the requested
   analysis. Do not claim that the library converts HTML to plain text.
4. Traverse `Children` for the MIME hierarchy. Use `Attachments` and
   `InlineResources` as immutable recursive views of those same nodes.
5. Persist diagnostic code, severity, and relevant context with the analytics
   record. Nested-part diagnostics remain on their child nodes.
6. Use `to_dict()` or `export_as_json()` when the complete canonical schema is
   wanted. Record `schema_version` and do not expect raw byte payloads in that
   serialization.
7. Keep integration code typed and small. Do not introduce a new runtime
   dependency without the user's approval.

Read [analytics-recipes.md](references/analytics-recipes.md) for participant,
thread, routing, content, attachment, and data-quality patterns.

## Test and verify

1. Test transformations and parser integrations with hard-coded `bytes`,
   `str`, `BytesIO`, or `StringIO`.
2. Reserve committed EML fixtures and filesystem behavior for functional tests.
3. Cover the user's important edge cases, including mixed body and attachment
   messages, duplicate headers, Unicode fields, malformed-but-recoverable
   messages, strict rejection, and configured resource limits.
4. Assert interpreted values and diagnostics. Assert raw preservation when the
   application depends on it.
5. Run the smallest relevant tests while developing, then the target project's
   required format, lint, type, test, and coverage checks before handoff.

Read [testing-patterns.md](references/testing-patterns.md) for representative
tests and fixture boundaries.

## Preserve these guardrails

- Do not use removed compatibility projections or separate attachment and
  address collection classes.
- Do not manually decode MIME transfer encodings or charsets that the parser
  already handles.
- Do not save attachments by default. When saving is requested, require an
  existing destination and rely on the library's safe-basename handling.
- Do not log or transmit email content, addresses, raw source, or attachment
  bytes without an explicit need and authorization.
- Do not close caller-owned streams passed to `parse_stream()`.
- Do not hide strict compliance failures as ordinary missing-file results.
