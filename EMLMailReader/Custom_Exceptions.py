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
