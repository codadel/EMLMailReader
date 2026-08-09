# Testing EMLMailReader integrations

## Keep unit tests in memory

Use hard-coded bytes or strings for transformation and parser-integration
tests:

```python
from EMLMailReader import MailReader


def test_extracts_participants_and_text() -> None:
    source = (
        b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
        b"From: Alice <alice@example.com>\r\n"
        b"To: Team: Bob <bob@example.com>;\r\n"
        b"Subject: Metrics\r\n"
        b"\r\n"
        b"Quarterly update"
    )

    message = MailReader().parse_bytes(source)

    assert [item.Email for item in message.From.Mailboxes] == ["alice@example.com"]
    assert [item.Email for item in message.To.Mailboxes] == ["bob@example.com"]
    assert message.TextBody == "Quarterly update"
```

Use `BytesIO` or `StringIO` to verify stream behavior. Assert that the
caller-owned stream remains open.

## Use functional tests for files

Use committed `.eml` fixtures for:

- `get_email()` behavior;
- exact real-world reproductions;
- attachment writes;
- logging files;
- missing, empty, and unreadable file handling.

Protect issue-regression fixtures from accidental normalization with a
checksum when byte identity matters. Never use private production email as a
fixture without explicit sanitization and approval.

## Cover meaningful edge cases

Select cases relevant to the application:

- body followed by an attachment;
- plain-text and HTML alternatives;
- nested messages and multipart containers;
- repeated headers and address groups;
- Unicode display names and subjects;
- malformed but recoverable fields with diagnostics;
- strict-mode `StandardsComplianceError`;
- message, header, depth, part-count, and decoded-body limits;
- unnamed or path-like attachment filenames.

## Assert the right layers

- Assert parsed values used by the application.
- Assert diagnostic code and severity for recovery behavior.
- Assert `RawSource` only when exact bytes are an application requirement.
- Assert attachment metadata without writing files in unit tests.
- Assert serialized `schema_version` when persisting the canonical schema.

Avoid snapshots that obscure which public contract failed.

## Validate generated code

Follow the target project's commands. At minimum, run focused tests plus its
formatter check, linter, type checker, and full test suite. Do not add broad
type ignores, lower coverage thresholds, or weaken checks to make generated
code pass.
