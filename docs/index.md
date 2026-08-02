# Parse EML files into useful Python data

EMLMailReader reads a local `.eml` file and returns an `RxMailMessage` object
containing its sender, recipients, subject, date, headers, body, MIME structure,
and decoded attachments.

!!! info "You are reading the v1 documentation"

    This portal describes EMLMailReader **1.0.4**. Use the version selector when
    you need documentation for another major release.

## Where the library fits

EMLMailReader v1 is useful when you already have EML files and want to:

- turn message metadata into records for analytics;
- inspect senders and recipient lists;
- count or extract attachments;
- process a directory of exported mail; or
- investigate parsing problems with optional logging.

It uses only the Python standard library at runtime and requires Python 3.12 or
newer.

## A first parse

```python
from EMLMailReader import MailReader

reader = MailReader()
message = reader.get_email("/data/mail/example.eml")

if message is None:
    print("The email could not be parsed")
else:
    print(message.Subject)
    print(message.From)
    print(message.Attachments.length())
```

`get_email()` reports an unreadable or missing file by returning `None`. Enable
logging when you need the underlying diagnostic message.

## Choose your next step

- [Install v1](getting-started/installation.md) and verify your environment.
- [Parse your first email](getting-started/first-email.md) and inspect the
  result safely.
- [Build analytics records](guides/analytics.md) without coupling your dataset
  to the library's object model.
- [Understand v1 limitations](concepts/v1-behavior.md) before processing
  untrusted or unusually large mailboxes.
- Open the [generated API reference](reference/index.md) for exact signatures.

## What v1 returns

The top-level result is an `RxMailMessage`. Addresses and attachments use small
collection objects with `length()` and `export_as_list()` methods. Multipart
messages additionally expose child MIME entities through `Children`.

The built-in `export_as_json()` method produces a compact metadata summary. It
does not include the message body or attachment bytes, so analytics pipelines
often build their own record instead.
