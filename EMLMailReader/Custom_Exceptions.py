"""Exceptions raised by EMLMailReader filesystem operations."""


class FileMissingError(Exception):
    """Report that an EML source file is unavailable.

    ``MailReader.get_email`` catches this exception and normally exposes the
    failure as a ``None`` result, but the type remains public for callers that
    use lower-level workflows.

    Attributes:
        filePath: Path that could not be found or accessed.
    """

    def __init__(self, filePath: str):
        """Store the unavailable file path."""
        self.filePath = filePath
        """The file path that was not found or is inaccessible."""

    def __str__(self) -> str:
        """Return an error message containing the unavailable file path."""
        line = self.__traceback__.tb_lineno if self.__traceback__ else "unknown"
        return f"Error occurred on line {line}:> File - '{self.filePath}' is either not available at location or not accessible."


class FolderNotAvailableError(Exception):
    """Report that an output directory is unavailable.

    Attachment saving and file logging require an existing target directory and
    raise this exception when that precondition is not met.

    Attributes:
        folderPath: Directory path that could not be used.
    """

    def __init__(self, folderPath: str):
        """Store the unavailable directory path."""
        self.folderPath = folderPath
        """The folder path that was not found or is inaccessible."""

    def __str__(self) -> str:
        """Return an error message containing the unavailable directory path."""
        line = self.__traceback__.tb_lineno if self.__traceback__ else "unknown"
        return f"Error occurred on line {line}:> Folder - '{self.folderPath}' is either not accessible or does not exist.."
