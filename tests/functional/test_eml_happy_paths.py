"""Successful end-to-end EML and filesystem workflows."""

import datetime
import logging
from base64 import b64encode
from collections.abc import Iterator
from hashlib import sha256
from pathlib import Path
from quopri import encodestring
from unittest.mock import patch

import pytest

from EMLMailReader import Logger, LoggingMode, MailReader, RxMailMessage
from EMLMailReader.Enumerations import LoggingLevel

pytestmark = pytest.mark.functional

ASSET_DIRECTORY = Path(__file__).parent / "assets"
EML_DIRECTORY = ASSET_DIRECTORY / "eml-files"
FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"
REGRESSION_DIRECTORY = Path(__file__).parent / "regressions"
PLAIN_MESSAGE = EML_DIRECTORY / "Test-Email-One.eml"
ISSUE_3_SOURCE = REGRESSION_DIRECTORY / "issue-3-body-and-attachment.eml"
ISSUE_3_SOURCE_SHA256 = (
    "87a6069217b8f6dca7a991384f4d9414549c12a13bf1bddabf5c0de4b960dd86"
)
ISSUE_3_BODY = "This email has both body text and an attachment\r\n"
REQUIRED = (
    b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\nFrom: Alice <alice@example.com>\r\n"
)
CASES = (
    (
        "Test-Email-One.eml",
        "Chris made appointment with Kenyon to prepare for deposition",
        "mk.balaji@gmail.com",
        "text/plain",
        0,
        0,
        0,
    ),
    (
        "Test-Email-Two.eml",
        "Fracassa call 11/1",
        "ted.chadwick@gmail.com",
        "text/plain",
        0,
        0,
        0,
    ),
    (
        "Test-Email-Three.eml",
        "document checklist for 189 Beavertail Rd",
        "ted.chadwick@gmail.com",
        "multipart/mixed",
        4,
        3,
        0,
    ),
    (
        "Test-Email-Four.eml",
        "View your Microsoft 365 Business Basic invoice",
        "microsoft-noreply@microsoft.com",
        "multipart/mixed",
        2,
        1,
        0,
    ),
    (
        "Test-Email-Five.eml",
        "Test-Email-5",
        "maheshkumaar.balaji@outlook.com",
        "multipart/mixed",
        2,
        1,
        0,
    ),
    (
        "Test-Email-Six.eml",
        "Test Email 6 - Sent via Gmail web",
        "maheshkumaar.balaji@gmail.com",
        "multipart/alternative",
        2,
        0,
        0,
    ),
    (
        "Test-Email-Seven.eml",
        "Re: Test Email 6 - Sent via Gmail web",
        "maheshkumaar.balaji@mkbdgs.com",
        "multipart/alternative",
        2,
        0,
        0,
    ),
    (
        "Test-Email-Eight.eml",
        "Test Mail 8 - Sent from Apple Mail",
        "maheshkumaar.balaji@gmail.com",
        "multipart/related",
        2,
        0,
        1,
    ),
)


def _close_logging_handlers() -> None:
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)


@pytest.fixture(autouse=True)
def reset_logging() -> Iterator[None]:
    _close_logging_handlers()
    yield
    _close_logging_handlers()


def _parse_file(tmp_path: Path, name: str, source: bytes) -> RxMailMessage:
    path = tmp_path / name
    path.write_bytes(source)
    message = MailReader().get_email(str(path))
    assert message is not None
    assert message.RawSource == source
    return message


@pytest.mark.parametrize(
    (
        "filename",
        "subject",
        "from_address",
        "media_type",
        "child_count",
        "attachment_count",
        "inline_count",
    ),
    CASES,
    ids=[case[0].removesuffix(".eml") for case in CASES],
)
def test_real_eml_files_parse_into_expected_message_tree(
    filename: str,
    subject: str,
    from_address: str,
    media_type: str,
    child_count: int,
    attachment_count: int,
    inline_count: int,
) -> None:
    message = MailReader().get_email(str(EML_DIRECTORY / filename))

    assert message is not None
    assert message.Subject == subject
    assert message.From.Mailboxes[0].Email == from_address
    assert message.ContentType.MediaType == media_type
    assert len(message.Children) == child_count
    assert len(message.Attachments) == attachment_count
    assert len(message.InlineResources) == inline_count
    assert message.RawSource
    assert not any(item.severity.value == "error" for item in message.Diagnostics)


def test_real_message_exposes_public_helpers() -> None:
    message = MailReader().get_email(str(PLAIN_MESSAGE))
    assert message is not None

    mailbox = message.From.Mailboxes[0]
    assert mailbox.to_dict()["email"] == mailbox.Email
    assert mailbox.to_header_value() == str(mailbox)
    assert message.Headers[0].to_dict()["name"]
    assert list(message.Headers)
    assert message.Headers.to_list()
    assert message.ContentType.get_parameter("missing", "fallback") == "fallback"
    assert str(message.ContentType) == message.ContentType.to_header_value()
    assert message.ContentType.to_dict()["media_type"] == "text/plain"
    assert message.to_dict()["schema_version"] == 2
    assert message.export_as_json()


def test_file_backed_message_entities_and_metadata(tmp_path: Path) -> None:
    nested = REQUIRED + b"Subject: nested\r\n\r\nbody"
    base64_message = _parse_file(
        tmp_path,
        "global-base64.eml",
        REQUIRED
        + b"MIME-Version: 1.0\r\n"
        + b"Content-Type: message/global\r\n"
        + b"Content-Transfer-Encoding: base64\r\n\r\n"
        + b64encode(nested),
    )
    assert base64_message.Children[0].Subject == "nested"

    quoted_message = _parse_file(
        tmp_path,
        "global-quoted.eml",
        REQUIRED
        + b"MIME-Version: 1.0\r\n"
        + b"Content-Type: message/global\r\n"
        + b"Content-Transfer-Encoding: quoted-printable\r\n\r\n"
        + encodestring(nested),
    )
    assert quoted_message.Children

    partial = _parse_file(
        tmp_path,
        "partial.eml",
        REQUIRED
        + b"MIME-Version: 1.0\r\n"
        + b'Content-Type: message/partial; id="part"; number=2; total=3\r\n\r\n'
        + b"fragment",
    )
    assert partial.MessagePartial is not None
    assert partial.to_dict()["message_partial"] is not None

    external = _parse_file(
        tmp_path,
        "external.eml",
        REQUIRED
        + b"MIME-Version: 1.0\r\n"
        + b'Content-Type: message/external-body; access-type=URL; URL="https://example.com"\r\n\r\n'
        + b"Content-Type: text/plain\r\n\r\n",
    )
    assert external.ExternalBodyAccess is not None
    assert external.to_dict()["external_body_access"] is not None


def test_attachment_save_sanitizes_name_and_writes_decoded_bytes(
    tmp_path: Path,
) -> None:
    message = MailReader().get_email(
        str(FIXTURE_DIRECTORY / "attachment-traversal.eml")
    )

    assert message is not None
    message.save_attachments(str(tmp_path))

    assert (tmp_path / "escape.bin").read_bytes() == b"payload"
    assert not (tmp_path.parent / "escape.bin").exists()


def test_nested_message_attachment_saves_child_source(tmp_path: Path) -> None:
    container = RxMailMessage()
    container.ContentType.parse('message/rfc822; name="nested.eml"')
    child = RxMailMessage()
    child.RawSource = b"nested message"
    container.Children.append(child)

    root = RxMailMessage()
    root.Children.append(container)
    root.save_attachments(str(tmp_path))

    assert (tmp_path / "nested.eml").read_bytes() == b"nested message"


def test_issue_3_preserves_body_when_attachment_follows() -> None:
    source = ISSUE_3_SOURCE.read_bytes()

    assert sha256(source).hexdigest() == ISSUE_3_SOURCE_SHA256

    message = MailReader().get_email(str(ISSUE_3_SOURCE))

    assert message is not None
    assert message.RawSource == source
    assert message.Subject == "An Email with a body and an attachment"
    assert message.Body == ISSUE_3_BODY
    assert message.TextBody == ISSUE_3_BODY
    assert message.HtmlBody == ""
    assert len(message.Children) == 2
    assert len(message.Attachments) == 1

    attachment = message.Attachments[0]
    assert attachment.Name == "find_x_lol.jpg"
    assert attachment.ContentType.MediaType == "image/jpeg"
    assert attachment.IsAttachment
    assert not any(
        diagnostic.severity.value == "error" for diagnostic in message.Diagnostics
    )


def test_file_logging_creates_timestamped_files_and_writes_entries(
    tmp_path: Path,
) -> None:
    first_time = datetime.datetime(2026, 1, 2, 3, 4, 5)
    second_time = datetime.datetime(2026, 1, 2, 3, 4, 6)

    with patch("EMLMailReader.Processing_Logs.datetime.datetime") as current:
        current.now.return_value = first_time
        first = Path(Logger.set_configuration(LoggingMode.FILE, str(tmp_path)))
        Logger.logentry("info", LoggingLevel.INFO)
        Logger.logentry("error", LoggingLevel.ERROR)
        Logger.logentry("critical", LoggingLevel.CRITICAL)
        Logger.logentry("debug", LoggingLevel.DEBUG)
        logging.shutdown()
        _close_logging_handlers()

        current.now.return_value = second_time
        second = Path(Logger.set_configuration(LoggingMode.FILE, str(tmp_path)))

    assert first != second
    assert first.exists()
    assert second.exists()
    content = first.read_text(encoding="utf-8")
    assert all(value in content for value in ("info", "error", "critical", "debug"))


def test_console_and_file_logging_have_formatters(tmp_path: Path) -> None:
    Logger.set_configuration(LoggingMode.CONSOLE)
    console_formatters = [
        handler.formatter
        for handler in logging.getLogger().handlers
        if handler.formatter is not None
    ]

    _close_logging_handlers()

    Logger.set_configuration(LoggingMode.FILE, str(tmp_path))
    file_formatters = [
        handler.formatter
        for handler in logging.getLogger().handlers
        if handler.formatter is not None
    ]

    assert console_formatters
    assert file_formatters
