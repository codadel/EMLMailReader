import datetime
import logging
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from EMLMailReader import FolderNotAvailableError, Logger, LoggingMode
from EMLMailReader.Enumerations import LoggingLevel

pytestmark = pytest.mark.functional


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


def test_file_logging_creates_timestamped_log_in_target_folder(
    tmp_path: Path,
) -> None:
    result = Path(Logger.set_configuration(LoggingMode.FILE, str(tmp_path)))

    assert result.parent == tmp_path
    assert result.name.startswith("EMLMailReader_Logs_")
    assert result.suffix == ".log"
    assert result.exists()


@pytest.mark.parametrize("target", ["", "/definitely/missing/log/folder"])
def test_file_logging_rejects_invalid_target_folder(target: str) -> None:
    with pytest.raises(FolderNotAvailableError) as error:
        Logger.set_configuration(LoggingMode.FILE, target)

    assert error.value.folderPath == target


def test_file_logging_uses_timestamp_for_unique_names(tmp_path: Path) -> None:
    first_time = datetime.datetime(2026, 1, 2, 3, 4, 5)
    second_time = datetime.datetime(2026, 1, 2, 3, 4, 6)

    with patch("EMLMailReader.Processing_Logs.datetime.datetime") as current:
        current.now.return_value = first_time
        first = Path(Logger.set_configuration(LoggingMode.FILE, str(tmp_path)))
        _close_logging_handlers()

        current.now.return_value = second_time
        second = Path(Logger.set_configuration(LoggingMode.FILE, str(tmp_path)))

    assert first != second
    assert first.exists()
    assert second.exists()


def test_log_entries_are_written_to_file(tmp_path: Path) -> None:
    log_file = Path(Logger.set_configuration(LoggingMode.FILE, str(tmp_path)))

    Logger.logentry("Test log message for file writing", LoggingLevel.INFO)
    logging.shutdown()

    content = log_file.read_text(encoding="utf-8")
    assert "Test log message for file writing" in content
    assert "INFO" in content


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
