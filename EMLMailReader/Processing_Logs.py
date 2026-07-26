import os
import logging
import datetime
from .Enumerations import LoggingMode, LoggingLevel
from .Custom_Exceptions import FolderNotAvailableError


class Logger:
    """
    A static utility class for managing logging configuration and output during EML processing.

    This class provides centralized logging functionality with support for console output,
    file output, or disabled logging. It integrates with Python's standard logging module
    to provide consistent log formatting and multiple output destinations.
    """

    @staticmethod
    def set_configuration(logging_mode: LoggingMode, target_folder: str = str()) -> str:
        """
        Configures the logging system with the specified output mode and destination.

        This method initializes Python's logging system with appropriate handlers,
        formatters, and output destinations. For file logging, it creates timestamped
        log files in the specified directory.

        :param logging_mode: Determines where log messages should be output (console, file, or disabled).
        :param target_folder: Directory path for log file creation (required only for FILE mode).
        :returns: Complete path to the created log file, or empty string for console/disabled modes.
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
        """
        Creates and outputs a log entry with the specified message and severity level.

        This method routes log messages to the appropriate Python logging function
        based on the specified logging level, ensuring consistent formatting and output.

        :param message: Text content of the log message to be recorded.
        :param logging_level: Severity level of the message (DEBUG, INFO, ERROR, CRITICAL).
        :returns: None - outputs the message through the configured logging system.
        """
        if logging_level == LoggingLevel.INFO:
            logging.info(message)
        elif logging_level == LoggingLevel.ERROR:
            logging.error(message)
        elif logging_level == LoggingLevel.CRITICAL:
            logging.critical(message)
        else:
            logging.debug(message)
