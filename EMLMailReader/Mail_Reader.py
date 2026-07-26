import os

from .Custom_Exceptions import FileMissingError
from .Enumerations import LoggingLevel, LoggingMode
from .Processing_Logs import Logger
from .RFC_Parser import StandardsParser
from .Rx_Mail_Message import RxMailMessage
from .Standards import ParserLimits, ParsingMode, StandardsComplianceError


class MailReader:
    """Public façade for parsing EML files, bytes, strings, and streams."""

    def __init__(
        self,
        logging_mode: LoggingMode = LoggingMode.NONE,
        TargetLoggingFolder: str = "",
        parsing_mode: ParsingMode | str = ParsingMode.MODERN,
        limits: ParserLimits | None = None,
    ):
        self.ParsingMode = parsing_mode
        self.LoggingMode = logging_mode
        self.__StandardsParser = StandardsParser(parsing_mode, limits)
        if logging_mode == LoggingMode.CONSOLE:
            Logger.set_configuration(LoggingMode.CONSOLE)
        elif logging_mode == LoggingMode.FILE:
            Logger.set_configuration(LoggingMode.FILE, TargetLoggingFolder)

    def get_email(self, emlPath: str) -> RxMailMessage | None:
        """Parse an EML file, returning ``None`` for file-system read failures."""
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
        """Parse an EML message without losing source octets."""
        message = self.__StandardsParser.parse(source)
        for diagnostic in self._all_diagnostics(message):
            level = LoggingLevel.ERROR if diagnostic.severity.value == "error" else LoggingLevel.INFO
            Logger.logentry(f"{diagnostic.code}: {diagnostic.message}", level)
        return message

    def parse_string(self, source: str, encoding: str = "utf-8") -> RxMailMessage:
        """Parse an in-memory message string using UTF-8 by default."""
        return self.parse_bytes(source.encode(encoding))

    def parse_stream(self, stream) -> RxMailMessage:
        """Parse a binary or text stream from its current position."""
        source = stream.read()
        if isinstance(source, str):
            source = source.encode("utf-8")
        return self.parse_bytes(source)

    @classmethod
    def _all_diagnostics(cls, message: RxMailMessage):
        yield from message.Diagnostics
        for child in message.Children:
            yield from cls._all_diagnostics(child)
