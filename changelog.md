# Changelog

This file records changes that have already been published to
[PyPI](https://pypi.org/project/emlmailreader/).

Do not add an unreleased section or reserve a future version number. Add a new
version entry only after that version is visible on PyPI.

## [2.0.0](https://pypi.org/project/emlmailreader/2.0.0/) - 2026-08-16

### What's Changed
* docs: add the versioned v1 documentation portal by @mkbalaji-dev in https://github.com/codadel/EMLMailReader/pull/5
* feat: deliver standards-compliant EML parser overhaul by @mkbalaji-dev in https://github.com/codadel/EMLMailReader/pull/4
* Releasing new version 2.0 by @mkbalaji-dev in https://github.com/codadel/EMLMailReader/pull/6


**Full Changelog**: https://github.com/codadel/EMLMailReader/compare/v1.0.4...v2.0.0

## [1.0.4](https://pypi.org/project/emlmailreader/1.0.4/) - 2026-07-10

### Added

- Added comprehensive module and public API documentation under `docs/`.
- Expanded automated tests for multipart messages, attachments, address
  headers, transfer encodings, malformed input, and logging behavior.
- Added `mise` development tasks and documented test and release workflows.
- Added an automated GitHub Actions release pipeline using PyPI Trusted
  Publishing.

### Changed

- Refreshed the README, project links, and generated API documentation.
- Removed the MkDocs dependency after moving to repository-hosted Markdown
  documentation.

### Fixed

- Preserved a multipart message's text body when a later attachment part did
  not contain a body.

## [1.0.3](https://pypi.org/project/emlmailreader/1.0.3/) - 2025-05-05

### Changed

- Refreshed the project branding and README formatting.
- Corrected repository, issue tracker, and documentation links.
- Made no parser behavior changes in this release.

## [1.0.2](https://pypi.org/project/emlmailreader/1.0.2/) - 2025-01-26

### Changed

- Moved the detailed API guide out of the README into dedicated
  documentation.
- Simplified the README and refreshed the project and source links.
- Cleaned repository metadata and development-only files.
- Made no parser behavior changes in this release.

## [1.0.1](https://pypi.org/project/emlmailreader/1.0.1/) - 2024-03-29

### Added

- Added explicit console, file, and disabled logging modes.
- Added broader parser tests, including messages produced by Gmail Web and
  Apple Mail.

### Changed

- Treated header names case-insensitively and preserved colons appearing
  inside header values.
- Distinguished Base64-encoded text bodies from binary and image attachments.
- Ignored unsupported MIME parameters instead of aborting message parsing.
- Rendered `Content-Type` values using normalized MIME header syntax.

### Fixed

- Corrected end-of-file and body-loop handling for messages without a trailing
  boundary or line.
- Improved decoding of encoded headers and Base64 text parts.

## [1.0.0](https://pypi.org/project/emlmailreader/1.0.0/) - 2024-02-17

### Added

- Published the initial Python 3.12+ release of `emlmailreader`.
- Added filesystem-based EML parsing into an `RxMailMessage` object.
- Added extraction of sender and recipient addresses, common message fields,
  remaining headers, decoded message bodies, nested MIME parts, and
  attachments.
- Added MIME `Content-Type` and `Content-Disposition` models.
- Added Base64 and quoted-printable decoding helpers.
- Added JSON export, attachment saving, processing logs, and library-specific
  parsing exceptions.
