import unittest
import sys
import traceback
from EMLMailReader import (
    InvalidEncodingError,
    FileMissingError,
    IncompleteHeaderError,
    FolderNotAvailableError,
    InvalidPropertyError
)


class TestCustomExceptions(unittest.TestCase):
    """
    A unit test case to check the custom exception classes exposed by the EMLMailReader library.
    """

    def test_invalid_encoding_error_with_encoded_value(self):
        """
        Test InvalidEncodingError exception initialization and string representation with encoded value.
        :returns: Does not return a value.
        """
        encoded_value = "=?utf-8?G?invalid_encoding?="

        try:
            raise InvalidEncodingError(encoded_value)
        except InvalidEncodingError as e:
            self.assertEqual(e.EncodedValue, encoded_value, "EncodedValue property should match the provided value.")
            self.assertEqual(e.Message, "Invalid encoding used", "Message property should have the default value.")
            error_str = str(e)
            self.assertIn("Invalid encoding used", error_str, "Error string should contain the message.")
            self.assertIn(encoded_value, error_str, "Error string should contain the encoded value.")
            self.assertIn("line", error_str.lower(), "Error string should contain line number information.")

    def test_invalid_encoding_error_without_encoded_value(self):
        """
        Test InvalidEncodingError exception initialization and string representation without encoded value.
        :returns: Does not return a value.
        """
        try:
            raise InvalidEncodingError()
        except InvalidEncodingError as e:
            self.assertEqual(e.EncodedValue, str(), "EncodedValue property should be empty string by default.")
            self.assertEqual(e.Message, "Invalid encoding used", "Message property should have the default value.")
            error_str = str(e)
            self.assertIn("Invalid encoding used", error_str, "Error string should contain the message.")
            self.assertNotIn("Encoded string causing the error", error_str, "Error string should not contain encoded value section when empty.")
            self.assertIn("line", error_str.lower(), "Error string should contain line number information.")

    def test_file_missing_error(self):
        """
        Test FileMissingError exception initialization and string representation.
        :returns: Does not return a value.
        """
        file_path = "/path/to/nonexistent/file.eml"

        try:
            raise FileMissingError(file_path)
        except FileMissingError as e:
            self.assertEqual(e.filePath, file_path, "filePath property should match the provided value.")
            error_str = str(e)
            self.assertIn(file_path, error_str, "Error string should contain the file path.")
            self.assertIn("not available at location", error_str, "Error string should contain appropriate message.")
            self.assertIn("line", error_str.lower(), "Error string should contain line number information.")

    def test_incomplete_header_error(self):
        """
        Test IncompleteHeaderError exception initialization and string representation.
        :returns: Does not return a value.
        """
        header_value = "malformed header without colon"
        line_number = 42

        try:
            raise IncompleteHeaderError(header_value, line_number)
        except IncompleteHeaderError as e:
            self.assertEqual(e.InvalidHeaderValue, header_value, "InvalidHeaderValue property should match the provided value.")
            self.assertEqual(e.LineInFile, line_number, "LineInFile property should match the provided value.")
            error_str = str(e)
            self.assertIn("Incomplete header", error_str, "Error string should contain appropriate message.")
            self.assertIn(str(line_number), error_str, "Error string should contain the line number.")
            self.assertIn("line", error_str.lower(), "Error string should contain line number information.")

    def test_folder_not_available_error(self):
        """
        Test FolderNotAvailableError exception initialization and string representation.
        :returns: Does not return a value.
        """
        folder_path = "/path/to/nonexistent/folder"

        try:
            raise FolderNotAvailableError(folder_path)
        except FolderNotAvailableError as e:
            self.assertEqual(e.folderPath, folder_path, "folderPath property should match the provided value.")
            error_str = str(e)
            self.assertIn(folder_path, error_str, "Error string should contain the folder path.")
            self.assertIn("not accessible or does not exist", error_str, "Error string should contain appropriate message.")
            self.assertIn("line", error_str.lower(), "Error string should contain line number information.")

    def test_invalid_property_error(self):
        """
        Test InvalidPropertyError exception initialization and string representation.
        :returns: Does not return a value.
        """
        property_name = "NonExistentProperty"

        try:
            raise InvalidPropertyError(property_name)
        except InvalidPropertyError as e:
            self.assertEqual(e.property_name, property_name, "property_name should match the provided value.")
            error_str = str(e)
            self.assertIn(property_name, error_str, "Error string should contain the property name.")
            self.assertIn("Invalid property", error_str, "Error string should contain appropriate message.")

    def test_exception_inheritance(self):
        """
        Test that all custom exceptions inherit from Exception base class.
        :returns: Does not return a value.
        """
        self.assertTrue(issubclass(InvalidEncodingError, Exception), "InvalidEncodingError should inherit from Exception.")
        self.assertTrue(issubclass(FileMissingError, Exception), "FileMissingError should inherit from Exception.")
        self.assertTrue(issubclass(IncompleteHeaderError, Exception), "IncompleteHeaderError should inherit from Exception.")
        self.assertTrue(issubclass(FolderNotAvailableError, Exception), "FolderNotAvailableError should inherit from Exception.")
        self.assertTrue(issubclass(InvalidPropertyError, Exception), "InvalidPropertyError should inherit from Exception.")

    def test_exception_raising_and_catching(self):
        """
        Test that custom exceptions can be properly raised and caught.
        :returns: Does not return a value.
        """
        # Test InvalidEncodingError
        with self.assertRaises(InvalidEncodingError):
            raise InvalidEncodingError("test")

        # Test FileMissingError
        with self.assertRaises(FileMissingError):
            raise FileMissingError("test_file.eml")

        # Test IncompleteHeaderError
        with self.assertRaises(IncompleteHeaderError):
            raise IncompleteHeaderError("test header", 1)

        # Test FolderNotAvailableError
        with self.assertRaises(FolderNotAvailableError):
            raise FolderNotAvailableError("test_folder")

        # Test InvalidPropertyError
        with self.assertRaises(InvalidPropertyError):
            raise InvalidPropertyError("test_property")


if __name__ == "__main__":
    unittest.main()
