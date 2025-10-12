class InvalidEncodingError(Exception):
    """
    A custom exception class to report invalid or unsupported text encoding errors.

    This exception is raised when the library encounters an encoding type that
    is not supported or when decoding fails due to invalid encoded content.
    """
    def __init__(self, EncodedValue: str = str()):
        self.EncodedValue = EncodedValue
        """The invalid encoded string that caused the error."""
        self.Message = "Invalid encoding used"
        """Descriptive error message."""

    def __str__(self):
        """
        Returns a formatted error message with line number and encoded value details.

        :returns: Formatted error message string.
        """
        if self.EncodedValue == str():
            return f"Error occurred on line {self.__traceback__.tb_lineno}:> {self.Message}."
        else:
            return f"Error occurred on line {self.__traceback__.tb_lineno}:> {self.Message}.\nEncoded string causing the error: {self.EncodedValue}."


class FileMissingError(Exception):
    """
    A custom exception class to report when a required file is missing or inaccessible.

    This exception is raised when attempting to read an EML file that doesn't exist
    at the specified path or when file access permissions are insufficient.
    """
    def __init__(self, filePath: str):
        self.filePath = filePath
        """The file path that was not found or is inaccessible."""

    def __str__(self):
        """
        Returns a formatted error message indicating the missing file path.

        :returns: Formatted error message string with file path details.
        """
        return f"Error occurred on line {self.__traceback__.tb_lineno}:> File - '{self.filePath}' is either not available at location or not accessible."


class IncompleteHeaderError(Exception):
    """
    A custom exception to report malformed or incomplete email headers in EML files.

    This exception is raised when a header line is found that doesn't conform to
    the expected format (missing colon separator, continuation without initial header, etc.).
    """
    def __init__(self, HeaderValue: str, LineInFile: int):
        self.InvalidHeaderValue = HeaderValue
        """The malformed header content that caused the error."""
        self.LineInFile = LineInFile
        """The line number in the EML file where the error occurred."""

    def __str__(self):
        """
        Returns a formatted error message with line number information.

        :returns: Formatted error message indicating the problematic line.
        """
        return f"Error occurred on line {self.__traceback__.tb_lineno}:> Incomplete header found on line {self.LineInFile} of EML File."


class FolderNotAvailableError(Exception):
    """
    A custom exception class to report when a required directory is missing or inaccessible.

    This exception is raised when attempting to access a folder that doesn't exist
    or when directory access permissions are insufficient for operations like saving attachments.
    """
    def __init__(self, folderPath: str):
        self.folderPath = folderPath
        """The folder path that was not found or is inaccessible."""

    def __str__(self):
        """
        Returns a formatted error message indicating the missing folder path.

        :returns: Formatted error message string with folder path details.
        """
        return f"Error occurred on line {self.__traceback__.tb_lineno}:> Folder - '{self.folderPath}' is either not accessible or does not exist.."


class InvalidPropertyError(Exception):
    """
    A custom exception class to report when an invalid or unsupported property is accessed.

    This exception is raised when attempting to set or access properties that don't exist
    on an object or when property values don't meet validation requirements.
    """
    def __init__(self, name: str):
        self.property_name = name
        """The name of the invalid property that was accessed."""

    def __str__(self):
        """
        Returns a formatted error message indicating the invalid property name.

        :returns: Formatted error message string with property name details.
        """
        return f"Invalid property '{self.property_name}' found."
