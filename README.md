![EMLMailReader logo](https://static.citadelofcode.com/emlmailreader/logo.png)

![PyPI version](https://img.shields.io/pypi/v/EMLMailReader.svg) ![Static Badge](https://img.shields.io/badge/powered_by-Codadel-orange)

# EMLMailReader

EMLMailReader parses local EML files into Python objects that are convenient
for inspection, batch processing, and analytics. Version 1.0.4 exposes message
headers, recipients, body text, MIME parts, and decoded attachment content
without runtime dependencies outside the Python standard library.

## Key Features

- Read common single-part and multipart EML messages.
- Decode Base64 and Quoted-Printable content.
- Access sender and recipient addresses as structured objects.
- Inspect and save decoded attachments.
- Convert message metadata to JSON.
- Enable console or file logging when diagnosing parse failures.

## Quick Start

### Installation

```console
python -m pip install "emlmailreader==1.0.4"
```

### Basic Usage

```python
from EMLMailReader import MailReader

reader = MailReader()
message = reader.get_email("/path/to/email.eml")

if message is None:
    print("The email could not be parsed")
else:
    print(message.Subject)
    print(message.From)
    print(message.To.export_as_list())
    print(message.Attachments.length())
```

## License

This library is distributed under the terms specified in the LICENSE file.

## Documentation

The [documentation portal](https://codadel.github.io/EMLMailReader/latest/) contains
task-oriented guides, v1 behavior notes, and the generated API reference.

## Support

For issues, questions, or contributions, please refer to the project repository.
