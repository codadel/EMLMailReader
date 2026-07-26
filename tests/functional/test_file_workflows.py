from pathlib import Path
from unittest.mock import patch

import pytest

from EMLMailReader import (
    FolderNotAvailableError,
    MailReader,
    ParsingMode,
    StandardsComplianceError,
)

pytestmark = pytest.mark.functional

FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"
PROVIDER_DIRECTORY = Path(__file__).parent / "assets" / "eml-files"
PLAIN_MESSAGE = PROVIDER_DIRECTORY / "Test-Email-One.eml"


def test_get_email_reads_an_eml_file() -> None:
    message = MailReader().get_email(str(PLAIN_MESSAGE))

    assert message is not None
    assert message.From.Mailboxes[0].Email == "mk.balaji@gmail.com"


def test_get_email_returns_none_for_missing_empty_and_read_error(
    tmp_path: Path,
) -> None:
    assert MailReader().get_email(str(tmp_path / "missing.eml")) is None

    empty = tmp_path / "empty.eml"
    empty.touch()
    assert MailReader().get_email(str(empty)) is None

    with patch("builtins.open", side_effect=PermissionError("denied")):
        assert MailReader().get_email(str(PLAIN_MESSAGE)) is None


def test_get_email_closes_file_after_parse_error(tmp_path: Path) -> None:
    source = tmp_path / "parse-error.eml"
    source.write_bytes(PLAIN_MESSAGE.read_bytes())

    with patch.object(MailReader, "parse_bytes", side_effect=RuntimeError("boom")):
        assert MailReader().get_email(str(source)) is None

    source.unlink()
    assert not source.exists()


def test_strict_file_parse_propagates_compliance_errors() -> None:
    source = FIXTURE_DIRECTORY / "strict-missing-date.eml"

    with pytest.raises(StandardsComplianceError):
        MailReader(parsing_mode=ParsingMode.STRICT).get_email(str(source))


def test_attachment_save_sanitizes_name_and_writes_decoded_bytes(
    tmp_path: Path,
) -> None:
    source = FIXTURE_DIRECTORY / "attachment-traversal.eml"
    message = MailReader().get_email(str(source))

    assert message is not None
    message.save_attachments(str(tmp_path))

    assert (tmp_path / "escape.bin").read_bytes() == b"payload"
    assert not (tmp_path.parent / "escape.bin").exists()


def test_unnamed_attachment_save_uses_fallback_name(tmp_path: Path) -> None:
    source = FIXTURE_DIRECTORY / "unnamed-attachment.eml"
    message = MailReader().get_email(str(source))

    assert message is not None
    message.save_attachments(str(tmp_path))

    assert (tmp_path / "attachment").read_bytes() == b"x"


def test_attachment_save_requires_an_existing_folder(tmp_path: Path) -> None:
    message = MailReader().get_email(
        str(FIXTURE_DIRECTORY / "attachment-traversal.eml")
    )
    missing = tmp_path / "missing"

    assert message is not None
    with pytest.raises(FolderNotAvailableError) as error:
        message.save_attachments(str(missing))

    assert error.value.folderPath == str(missing)
