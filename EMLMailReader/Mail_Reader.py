"""Public parsing facade for files and in-memory Internet messages."""

import os
from collections.abc import Iterator
from typing import IO

from .Custom_Exceptions import FileMissingError
from .Enumerations import LoggingLevel, LoggingMode
from .Processing_Logs import Logger
from .RFC_Parser import StandardsParser
from .Rx_Mail_Message import RxMailMessage
from .Standards import (
    ParseDiagnostic,
    ParserLimits,
    ParsingMode,
    StandardsComplianceError,
)


class MailReader:
    """Configure and execute standards-aware EML parsing.

    A reader owns one parser configuration, including its receiver/strict mode,
    resource limits, and optional diagnostic logging destination.

    Attributes:
        ParsingMode: Mode value supplied when the reader was created.
        LoggingMode: Configured diagnostic logging destination.
    """

    def __init__(
        self,
        logging_mode: LoggingMode = LoggingMode.NONE,
        TargetLoggingFolder: str = "",
        parsing_mode: ParsingMode | str = ParsingMode.MODERN,
        limits: ParserLimits | None = None,
    ) -> None:
        """Initialize a reusable parser facade.

        Args:
            logging_mode: Destination for parser diagnostic log messages.
            TargetLoggingFolder: Existing directory used by file logging.
            parsing_mode: Receiver behavior or strict conformance enforcement.
            limits: Resource guards; defaults to :class:`ParserLimits`.

        Raises:
            FolderNotAvailableError: If file logging is requested with an
                unavailable target directory.
        """
        self.ParsingMode = parsing_mode
        self.LoggingMode = logging_mode
        self.__StandardsParser = StandardsParser(parsing_mode, limits)
        if logging_mode == LoggingMode.CONSOLE:
            Logger.set_configuration(LoggingMode.CONSOLE)
        elif logging_mode == LoggingMode.FILE:
            Logger.set_configuration(LoggingMode.FILE, TargetLoggingFolder)

    def get_email(self, emlPath: str) -> RxMailMessage | None:
        """Read and parse an EML file.

        Args:
            emlPath: Path to the source EML file.

        Returns:
            The parsed message, or ``None`` when the file is missing, empty, or
            cannot be read.

        Raises:
            StandardsComplianceError: If strict parsing finds an error-level
                diagnostic.
        """
        eml_file = None
        try:
            if not os.path.exists(emlPath):
                raise FileMissingError(emlPath)
            eml_file = open(emlPath, "rb")
            source = eml_file.read()
            if not source:
                return None
            return self.parse_bytes(source)
        except StandardsComplianceError:
            raise
        except Exception as error:
            Logger.logentry(
                f"An exception occurred while reading contents from EML file: {error}",
                LoggingLevel.ERROR,
            )
            return None
        finally:
            if eml_file is not None:
                eml_file.close()

    def parse_bytes(self, source: bytes) -> RxMailMessage:
        """Parse wire bytes while preserving the exact root source octets.

        Parser diagnostics remain attached to their MIME nodes and are also
        forwarded to the configured logger.

        Args:
            source: Complete Internet message bytes.

        Returns:
            The root :class:`RxMailMessage`.

        Raises:
            StandardsComplianceError: If strict parsing finds an error-level
                diagnostic.
        """
        message = self.__StandardsParser.parse(source)
        for diagnostic in self._all_diagnostics(message):
            level = (
                LoggingLevel.ERROR
                if diagnostic.severity.value == "error"
                else LoggingLevel.INFO
            )
            Logger.logentry(f"{diagnostic.code}: {diagnostic.message}", level)
        return message

    def parse_string(self, source: str, encoding: str = "utf-8") -> RxMailMessage:
        """Encode and parse an in-memory Internet message string.

        Args:
            source: Complete message text.
            encoding: Encoding used to create parser input bytes.

        Returns:
            The parsed root message.
        """
        return self.parse_bytes(source.encode(encoding))

    def parse_stream(self, stream: IO[bytes] | IO[str]) -> RxMailMessage:
        """Read and parse a binary or text stream from its current position.

        Text streams are encoded as UTF-8. The caller retains ownership of the
        stream and is responsible for closing it.

        Args:
            stream: File-like object whose ``read()`` returns bytes or text.

        Returns:
            The parsed root message.
        """
        source = stream.read()
        if isinstance(source, str):
            source = source.encode("utf-8")
        return self.parse_bytes(source)

    @classmethod
    def _all_diagnostics(cls, message: RxMailMessage) -> Iterator[ParseDiagnostic]:
        """Yield diagnostics from a message and all descendant MIME nodes."""
        yield from message.Diagnostics
        for child in message.Children:
            yield from cls._all_diagnostics(child)
