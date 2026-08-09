# Migrating from EMLMailReader v1.0.4

Treat migration as a model change, not a mechanical import rename. Confirm the
installed library exposes the canonical API before modifying user code.

## Replace legacy concepts

| Legacy concept | Canonical approach |
| --- | --- |
| Separate attachment objects and collections | `RxMailMessage.Attachments`, a tuple view over MIME nodes |
| Separate inline-resource representation | `RxMailMessage.InlineResources` |
| Address collection variants | `AddressList` and `.Mailboxes` |
| `HeaderFields` or a single-value header mapping | Ordered `Headers`, `get_all()`, and `occurrences()` |
| `FromAddresses` | `From` |
| `SenderAddress` | `Sender` |
| `ReplyToAddresses` | `ReplyTo` |
| `ToAddresses` | `To` |
| `EffectiveContentType` | `ContentType` |
| `PreferredBody` | Choose `Body`, `TextBody`, or `HtmlBody` explicitly |
| `compatibility_mode` | One canonical model; choose a `ParsingMode` |
| Legacy JSON projection | Recursive schema from `to_dict()` with `schema_version == 2` |

Do not recreate removed types as local compatibility wrappers unless the user
explicitly needs a temporary migration boundary.

## Review behavior, not only names

1. Replace manual header dictionaries with ordered, duplicate-preserving
   access.
2. Decide whether address-group boundaries matter or `.Mailboxes` is the
   intended flattened view.
3. Update attachment code because attachment entries are complete
   `RxMailMessage` MIME nodes.
4. Select body semantics explicitly.
5. Add handling for diagnostics and strict compliance failures.
6. Decide whether raw source and decoded payload bytes should be retained.
7. Update persisted JSON consumers for schema version 2.

## Migrate tests

Keep parser and transformation unit tests filesystem-free with in-memory
messages. Move real EML and file-writing cases to functional tests. Add a
before-and-after fixture for every business-critical v1 behavior, then assert
the canonical structured result rather than recreating the legacy projection.

## Manage rollout

Pin the expected library major version. Avoid running one analytics dataset
through mixed v1 and canonical schemas. For staged migrations, record the
parser package version and output schema version with each produced dataset.
