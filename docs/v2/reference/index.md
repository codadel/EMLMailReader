# API reference

The reference is split into two layers:

- focused pages explain how each public type behaves; and
- generated pages show signatures and docstrings from the v2 source code.

## Parsing and message model

- [MailReader](MailReader.md)
- [RxMailMessage](RxMailMessage.md)
- [Generated core API](generated-core.md)

## Addresses, headers, and structured values

- [MailAddress](MailAddress.md)
- [AddressList](AddressList.md)
- [Structured types](StructuredTypes.md)
- [Generated structured API](generated-standards.md)

## MIME values

- [ContentType](ContentType.md)
- [ContentDisposition](ContentDisposition.md)
- [Generated MIME API](generated-mime.md)

## Utilities and failures

- [TextEncoding](TextEncoding.md)
- [Logger](Logger.md)
- [Enumerations](Enumerations.md)
- [Exceptions](Exceptions.md)
- [Generated utility API](generated-utilities.md)

All supported public symbols are exported from `EMLMailReader`, except the
internal `LoggingLevel` enum.
