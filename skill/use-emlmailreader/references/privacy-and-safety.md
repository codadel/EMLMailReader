# Privacy and safety

## Minimize retained data

Email commonly contains personal data, secrets, legal material, and
attachments. Collect the minimum necessary fields. Prefer counts, presence
flags, domains, or hashes when the analysis does not require content.

Document whether the application retains:

- full filesystem paths;
- raw message bytes;
- sender and recipient addresses;
- subjects or bodies;
- decoded attachment bytes;
- parser diagnostics that may quote source context.

## Keep content local by default

Do not send raw email, bodies, headers, addresses, or attachments to an
external model, API, telemetry service, or shared log without explicit
authorization. Redact or aggregate fields before external processing when
possible.

## Treat input as hostile

Configure `ParserLimits` for messages from untrusted sources. Bound complete
message size, header size and count, MIME depth, part count, and decoded part
size. Keep limits active even when modern parsing recovers from syntax errors.

Do not render HTML, execute embedded content, or open attachments as part of
parsing or analytics. EMLMailReader parses data; it does not make content safe
to execute.

## Handle attachments deliberately

Inspect attachment metadata in memory unless files are required. When saving:

1. Require an existing, dedicated output directory.
2. Use `save_attachments()` so names are reduced to safe basenames.
3. Expect existing same-name files to be overwritten and define a collision
   policy when that matters.
4. Apply downstream malware or content scanning appropriate to the system.

Do not treat a filename or declared media type as trustworthy.

## Log safely

Prefer structured outcome and diagnostic codes over complete message values.
Do not log raw sources, bodies, addresses, or decoded payloads by default.
Ensure file logging destinations already exist and follow the application's
access-control and retention policies.

## Make failures auditable

Keep missing/unreadable files, strict standards failures, resource-limit
violations, and transformation errors distinguishable. Preserve enough source
identity to investigate an outcome without placing sensitive content in the
analytics record.
