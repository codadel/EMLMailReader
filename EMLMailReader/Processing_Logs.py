"""Configuration and routing helpers for parser diagnostic logging."""

import os
import logging
import datetime

from .Enumerations import LoggingMode, LoggingLevel
from .Custom_Exceptions import FolderNotAvailableError


class Logger:
    """Configure and write parser diagnostics through Python's root logger.

    The utility is stateless. Console and file configuration deliberately
    replace existing root handlers so repeated reader configuration is
    deterministic.
    """

    @staticmethod
    def set_configuration(logging_mode: LoggingMode, target_folder: str = str()) -> str:
        """Configure console, file, or disabled parser logging.

        Args:
            logging_mode: Desired :class:`LoggingMode`.
            target_folder: Existing directory for a timestamped log file.

        Returns:
            Created log path for file mode, otherwise an empty string.

        Raises:
            FolderNotAvailableError: If file mode has no usable target directory.
        """
        complete_file_path = str()
        if logging_mode == LoggingMode.CONSOLE:
            logging.basicConfig(
                level=logging.DEBUG,
                datefmt="%Y-%m-%d %H-%M-%S",
                format="%(asctime)s %(levelname)s %(name)s %(message)s",
                force=True,
            )
        elif logging_mode == LoggingMode.FILE:
            if target_folder != str() and os.path.exists(target_folder):
                _CurrentDateTime = datetime.datetime.now()
                file_name = f"EMLMailReader_Logs_{_CurrentDateTime.year}{_CurrentDateTime.month}{_CurrentDateTime.day}_{_CurrentDateTime.hour}{_CurrentDateTime.minute}{_CurrentDateTime.second}.log"
                complete_file_path = os.path.join(target_folder, file_name)
                logging.basicConfig(
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H-%M-%S",
                    format="%(asctime)s %(levelname)s %(name)s %(message)s",
                    encoding="utf-8",
                    filename=complete_file_path,
                    force=True,
                )
            else:
                raise FolderNotAvailableError(target_folder)
        return complete_file_path

    @staticmethod
    def logentry(message: str, logging_level: LoggingLevel):
        """Write one message at the requested library logging severity.

        Args:
            message: Log message text.
            logging_level: Severity mapped to the corresponding Python logging
                function. Unknown values fall back to debug.
        """
        if logging_level == LoggingLevel.INFO:
            logging.info(message)
        elif logging_level == LoggingLevel.ERROR:
            logging.error(message)
        elif logging_level == LoggingLevel.CRITICAL:
            logging.critical(message)
        else:
            logging.debug(message)
