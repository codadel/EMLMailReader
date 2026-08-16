![EMLMailReader logo](https://static.citadelofcode.com/emlmailreader/logo.png)

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Powered by Codadel](https://img.shields.io/badge/powered_by-Codadel-orange)](https://github.com/codadel)

# EMLMailReader

EMLMailReader parses local EML files and in-memory Internet messages into
structured Python objects for inspection, batch processing, and analytics.
The current release line is v2 and has no runtime dependencies outside the
Python standard library.

## Key Features

- Read EML files, bytes, strings, and streams.
- Inspect headers, sender and recipient addresses, message bodies, MIME parts,
  and attachments.
- Preserve useful source information while decoding message content.
- Record recoverable parsing problems or enforce strict validation.
- Export parsed message data for downstream analytics.
- Use the package with Python 3.12 or newer and inline type information.

## Quick Start

### Installation

```console
python -m pip install "emlmailreader>=2,<3"
```

Pin the major version in production so a future breaking release does not
change your analytics records unexpectedly.

### Basic Usage

```python
from EMLMailReader import MailReader

message = MailReader().get_email("/path/to/email.eml")

if message is None:
    raise RuntimeError("The email could not be read")

print(message.Subject)
print([mailbox.Email for mailbox in message.From.Mailboxes])
print(message.TextBody)
```

## License

This library is distributed under the terms specified in the
[LICENSE](LICENSE) file.

## Documentation

The [documentation portal](https://codadel.github.io/EMLMailReader/latest/)
contains installation guidance, analytics examples, versioned behavior notes,
migration guidance, and the generated API reference. Use its version selector
to open the v1.0.4 or v2 documentation.

## AI-Assisted Development

The repository includes a reusable
[use-emlmailreader skill](https://github.com/codadel/EMLMailReader/tree/develop/skill/use-emlmailreader)
for AI agents that build Python parsing, ingestion, or analytics code with
this library. It covers recommended API patterns, testing practices,
migration guidance, and privacy-aware handling. Follow your AI tool's normal
process for installing and using repository skills.

## Support

For issues and feature requests, use the
[GitHub issue tracker](https://github.com/codadel/EMLMailReader/issues).
