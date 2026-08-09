"""End-to-end EML and filesystem workflows that intentionally raise errors."""

from pathlib import Path

import pytest

from EMLMailReader import (
    DiagnosticSeverity,
    FolderNotAvailableError,
    Logger,
    LoggingMode,
    MailReader,
    ParsingMode,
    StandardsComplianceError,
)

pytestmark = pytest.mark.functional

FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"


def test_strict_file_parse_raises_compliance_error() -> None:
    source = FIXTURE_DIRECTORY / "strict-missing-date.eml"

    with pytest.raises(StandardsComplianceError) as error:
        MailReader(parsing_mode=ParsingMode.STRICT).get_email(str(source))

    assert any(
        diagnostic.code == "MissingRequiredDate"
        and diagnostic.severity == DiagnosticSeverity.ERROR
        for diagnostic in error.value.diagnostics
    )


def test_attachment_save_requires_existing_folder(tmp_path: Path) -> None:
    message = MailReader().get_email(
        str(FIXTURE_DIRECTORY / "attachment-traversal.eml")
    )
    missing = tmp_path / "missing"

    assert message is not None
    with pytest.raises(FolderNotAvailableError) as error:
        message.save_attachments(str(missing))

    assert error.value.folderPath == str(missing)


@pytest.mark.parametrize("target", ["", "/definitely/missing/log/folder"])
def test_file_logging_rejects_invalid_target_folder(target: str) -> None:
    with pytest.raises(FolderNotAvailableError) as error:
        Logger.set_configuration(LoggingMode.FILE, target)

    assert error.value.folderPath == target
