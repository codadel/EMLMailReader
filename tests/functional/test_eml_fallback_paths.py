"""Recoverable end-to-end EML workflows that return fallback results."""

from pathlib import Path
from unittest.mock import patch

import pytest

from EMLMailReader import (
    AddressList,
    MailReader,
    ParserLimits,
    ParsingMode,
    RxMailMessage,
)

pytestmark = pytest.mark.functional

ASSET_DIRECTORY = Path(__file__).parent / "assets"
FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"
PLAIN_MESSAGE = ASSET_DIRECTORY / "eml-files" / "Test-Email-One.eml"
REQUIRED = (
    b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\nFrom: Alice <alice@example.com>\r\n"
)


def _parse_file(
    tmp_path: Path,
    name: str,
    source: bytes,
    *,
    parsing_mode: ParsingMode | str = ParsingMode.MODERN,
    limits: ParserLimits | None = None,
) -> RxMailMessage:
    path = tmp_path / name
    path.write_bytes(source)
    message = MailReader(parsing_mode=parsing_mode, limits=limits).get_email(str(path))
    assert message is not None
    assert message.RawSource == source
    return message


def test_get_email_returns_none_for_missing_empty_and_read_error(
    tmp_path: Path,
) -> None:
    assert MailReader().get_email(str(tmp_path / "missing.eml")) is None

    empty = tmp_path / "empty.eml"
    empty.touch()
    assert MailReader().get_email(str(empty)) is None

    with patch("builtins.open", side_effect=PermissionError("denied")):
        assert MailReader().get_email(str(PLAIN_MESSAGE)) is None


def test_get_email_returns_none_and_closes_file_after_parse_error(
    tmp_path: Path,
) -> None:
    source = tmp_path / "parse-error.eml"
    source.write_bytes(PLAIN_MESSAGE.read_bytes())

    with patch.object(MailReader, "parse_bytes", side_effect=RuntimeError("boom")):
        assert MailReader().get_email(str(source)) is None

    source.unlink()
    assert not source.exists()


def test_unnamed_attachment_save_uses_fallback_name(tmp_path: Path) -> None:
    message = MailReader().get_email(str(FIXTURE_DIRECTORY / "unnamed-attachment.eml"))

    assert message is not None
    message.save_attachments(str(tmp_path))

    assert (tmp_path / "attachment").read_bytes() == b"x"


def test_file_backed_mime_tree_limits_and_leaf_decoding(tmp_path: Path) -> None:
    source = REQUIRED + (
        b"MIME-Version: 1.0\r\n"
        b"Content-Type: multipart/mixed; boundary=x\r\n\r\n"
        b"--x\r\nContent-Type: text/plain\r\n\r\none\r\n"
        b"--x\r\nContent-Type: text/plain\r\n\r\ntwo\r\n--x--\r\n"
    )
    part_limited = _parse_file(
        tmp_path,
        "part-limit.eml",
        source,
        limits=ParserLimits(max_parts=2),
    )
    assert "MimePartLimitExceeded" in {item.code for item in part_limited.Diagnostics}

    root_limited = _parse_file(
        tmp_path,
        "root-part-limit.eml",
        source,
        limits=ParserLimits(max_parts=0),
    )
    assert "MimePartLimitExceeded" in {item.code for item in root_limited.Diagnostics}

    depth_limited = _parse_file(
        tmp_path,
        "depth-limit.eml",
        source,
        limits=ParserLimits(max_mime_depth=0),
    )
    assert "MimeDepthLimitExceeded" in {
        item.code for child in depth_limited.Children for item in child.Diagnostics
    }

    invalid_text = _parse_file(
        tmp_path,
        "invalid-text.eml",
        REQUIRED
        + b"MIME-Version: 1.0\r\n"
        + b"Content-Type: text/plain; charset=x-unknown\r\n\r\n\xff",
        limits=ParserLimits(max_decoded_part_bytes=0),
    )
    assert invalid_text.Body == "�"
    assert {"DecodedPartLimitExceeded", "InvalidCharsetData"} <= {
        item.code for item in invalid_text.Diagnostics
    }


def test_file_backed_validation_diagnostics(tmp_path: Path) -> None:
    modern = _parse_file(
        tmp_path,
        "unknown-mode.eml",
        REQUIRED + b"\r\nbody",
        parsing_mode="unsupported",
    )
    assert modern.Body == "body"

    invalid = _parse_file(
        tmp_path,
        "invalid-fields.eml",
        b"Date: invalid\r\n"
        b"From: a@example.com, b@example.com\r\n"
        b"Sender: Group: a@example.com, b@example.com;\r\n"
        b"Message-ID: invalid\r\n"
        b"Subject: first\r\nSubject: second\r\n"
        b"Resent-To: recipient@example.com\r\n"
        b"MIME-Version: invalid\r\n"
        b"Content-Type: multipart/mixed\r\n"
        b"Content-Type: text/plain\r\n\r\n" + b"x" * 999,
    )
    codes = {item.code for item in invalid.Diagnostics}
    assert {
        "DuplicateSingletonHeader",
        "DuplicateMIMEHeader",
        "InvalidDate",
        "InvalidMessageID",
        "InvalidMIMEVersion",
        "InvalidSenderGroup",
        "IncompleteResentBlock",
        "LineTooLong",
    } <= codes

    route = _parse_file(
        tmp_path,
        "obsolete-route.eml",
        b"Date: 21 Nov 97 09:55:06 GMT\r\n"
        b"From: <@old.example:alice@example.com>\r\n\r\n",
    )
    assert "ObsoleteAddressRoute" in {item.code for item in route.Diagnostics}
    assert route.Date is not None and route.Date.obsolete

    bare_lf = _parse_file(
        tmp_path,
        "source-diagnostics.eml",
        b"Date: Fri, 21 Nov 1997 09:55:06 -0600\n"
        b"From: alice@example.com\nX-Bad: \xff\nX-Extra: value\n\nbody",
        limits=ParserLimits(
            max_message_bytes=20,
            max_header_bytes=10,
            max_header_count=1,
        ),
    )
    assert {
        "MessageSizeLimitExceeded",
        "HeaderSizeLimitExceeded",
        "HeaderCountLimitExceeded",
        "InvalidUTF8Header",
        "ObsoleteLineEnding",
    } <= {item.code for item in bare_lf.Diagnostics}

    missing_mime_version = _parse_file(
        tmp_path,
        "missing-mime-version.eml",
        REQUIRED + b"Content-Type: text/plain\r\n\r\nbody",
    )
    assert "MissingMIMEVersion" in {
        item.code for item in missing_mime_version.Diagnostics
    }

    unsupported_mime_version = _parse_file(
        tmp_path,
        "unsupported-mime-version.eml",
        REQUIRED + b"MIME-Version: 2.0\r\nContent-Type: text/plain\r\n\r\nbody",
    )
    assert "UnsupportedMIMEVersion" in {
        item.code for item in unsupported_mime_version.Diagnostics
    }

    missing_sender = _parse_file(
        tmp_path,
        "missing-sender.eml",
        b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
        b"From: a@example.com, b@example.com\r\n\r\nbody",
    )
    assert "MissingRequiredSender" in {item.code for item in missing_sender.Diagnostics}

    real_address_list = AddressList
    failed = False

    def fail_one_address(raw_value: str = "") -> AddressList:
        nonlocal failed
        if raw_value and not failed:
            failed = True
            raise ValueError("invalid address list")
        return real_address_list(raw_value)

    with patch(
        "EMLMailReader.RFC_Parser.AddressList",
        side_effect=fail_one_address,
    ):
        recovered_address = _parse_file(
            tmp_path,
            "recovered-address.eml",
            REQUIRED + b"To: recipient@example.com\r\n\r\nbody",
        )
    assert "InvalidAddressList" in {item.code for item in recovered_address.Diagnostics}


@pytest.mark.parametrize(
    ("name", "content_type", "expected_code"),
    (
        ("missing-boundary.eml", b"multipart/mixed", "MissingMultipartBoundary"),
        (
            "long-boundary.eml",
            b"multipart/mixed; boundary=" + b"x" * 71,
            "MultipartBoundaryTooLong",
        ),
        (
            "invalid-partial.eml",
            b"message/partial; id=x; number=2; total=1",
            "InvalidMessagePartialTotal",
        ),
        (
            "missing-partial.eml",
            b"message/partial; number=0",
            "InvalidMessagePartialParameters",
        ),
        (
            "external-access.eml",
            b"message/external-body",
            "MissingExternalBodyAccessType",
        ),
    ),
)
def test_file_backed_mime_parameter_validation(
    tmp_path: Path,
    name: str,
    content_type: bytes,
    expected_code: str,
) -> None:
    message = _parse_file(
        tmp_path,
        name,
        REQUIRED
        + b"MIME-Version: 1.0\r\nContent-Type: "
        + content_type
        + b"\r\n\r\nbody",
    )
    assert expected_code in {item.code for item in message.Diagnostics}


def test_invalid_composite_encoding_returns_diagnostic(tmp_path: Path) -> None:
    composite = _parse_file(
        tmp_path,
        "composite.eml",
        REQUIRED
        + b"MIME-Version: 1.0\r\n"
        + b"Content-Type: message/rfc822\r\n"
        + b"Content-Transfer-Encoding: base64\r\n\r\nbroken",
    )
    assert "InvalidCompositeTransferEncoding" in {
        item.code for item in composite.Diagnostics
    }


def test_resent_and_trace_recovery_is_serialized(tmp_path: Path) -> None:
    message = _parse_file(
        tmp_path,
        "resent.eml",
        REQUIRED
        + b"Return-Path: <first@example.com>\r\n"
        + b"Received: by first.example.com\r\n"
        + b"X-Break: one\r\n"
        + b"Return-Path: <second@example.com>\r\n"
        + b"Received: by second.example.com\r\n"
        + b"Resent-Date: Fri, 21 Nov 1997 10:00:00 -0600\r\n"
        + b"Resent-From: a@example.com, b@example.com\r\n"
        + b"Resent-Date: Fri, 21 Nov 1997 11:00:00 -0600\r\n"
        + b"Resent-From: sender@example.com\r\n\r\nbody",
    )
    assert len(message.TraceBlocks) == 2
    assert len(message.ResentBlocks) == 2
    assert "MissingRequiredResentSender" in {item.code for item in message.Diagnostics}
    exported = message.to_dict()
    assert exported["trace_blocks"]
    assert exported["resent_blocks"]


def test_diagnostics_are_serialized_with_fallback_message(tmp_path: Path) -> None:
    message = _parse_file(
        tmp_path,
        "diagnostic.eml",
        b"From: alice@example.com\r\n\r\nbody",
    )
    exported = message.to_dict()
    assert exported["diagnostics"]
    assert message.Date is None
