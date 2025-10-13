import unittest
import tempfile
import os
import logging
import shutil
from unittest.mock import patch, MagicMock
from EMLMailReader import Logger, LoggingMode, FolderNotAvailableError
from EMLMailReader.Enumerations import LoggingLevel


class TestProcessingLogs(unittest.TestCase):
    """
    A unit test case to check the Logger class methods exposed by the EMLMailReader library.
    """

    def setUp(self):
        """
        Set up test environment with temporary directories and reset logging configuration.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        # Clear any existing logging configuration
        self.close_logging_handlers()

    def tearDown(self):
        """
        Clean up temporary directories and reset logging configuration.
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        # Clear logging configuration after tests
        self.close_logging_handlers()

    def close_logging_handlers(self):
        """
        Close all logging handlers to release file resources.
        """
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)

    def test_set_configuration_console_mode(self):
        """
        Test Logger.set_configuration() with CONSOLE mode.
        :returns: Does not return a value.
        """
        result = Logger.set_configuration(LoggingMode.CONSOLE)

        # Should return empty string for console mode
        self.assertEqual(result, str(), "Console mode should return empty string.")

        # Check that logging is configured
        logger = logging.getLogger()
        self.assertTrue(len(logger.handlers) > 0, "Console mode should configure logging handlers.")
        self.assertEqual(logger.level, logging.DEBUG, "Console mode should set logging level to DEBUG.")

    def test_set_configuration_file_mode_valid_folder(self):
        """
        Test Logger.set_configuration() with FILE mode and valid target folder.
        :returns: Does not return a value.
        """
        result = Logger.set_configuration(LoggingMode.FILE, self.temp_dir)

        # Should return a valid file path
        self.assertNotEqual(result, str(), "File mode should return non-empty string.")
        self.assertTrue(result.startswith(self.temp_dir), "Returned path should be in target directory.")
        self.assertTrue(result.endswith(".log"), "Returned path should end with .log.")
        self.assertTrue(os.path.exists(result), "Log file should be created.")

        # Check filename format
        filename = os.path.basename(result)
        self.assertTrue(filename.startswith("EMLMailReader_Logs_"), "Filename should have correct prefix.")

    def test_set_configuration_file_mode_invalid_folder(self):
        """
        Test Logger.set_configuration() with FILE mode and invalid target folder.
        :returns: Does not return a value.
        """
        with self.assertRaises(FolderNotAvailableError) as context:
            Logger.set_configuration(LoggingMode.FILE, self.non_existent_dir)

        self.assertEqual(context.exception.folderPath, self.non_existent_dir,
                        "Exception should contain the invalid folder path.")

    def test_set_configuration_file_mode_empty_folder(self):
        """
        Test Logger.set_configuration() with FILE mode and empty target folder.
        :returns: Does not return a value.
        """
        with self.assertRaises(FolderNotAvailableError) as context:
            Logger.set_configuration(LoggingMode.FILE, str())

        self.assertEqual(context.exception.folderPath, str(),
                        "Exception should contain the empty folder path.")

    def test_set_configuration_none_mode(self):
        """
        Test Logger.set_configuration() with NONE mode (implicit - any other mode).
        :returns: Does not return a value.
        """
        # Using a custom enum value or invalid mode should not configure logging
        result = Logger.set_configuration(LoggingMode.NONE)

        self.assertEqual(result, str(), "NONE mode should return empty string.")

    @patch('logging.info')
    def test_logentry_info_level(self, mock_info):
        """
        Test Logger.logentry() with INFO logging level.
        :returns: Does not return a value.
        """
        test_message = "This is an info message"
        Logger.logentry(test_message, LoggingLevel.INFO)

        mock_info.assert_called_once_with(test_message)

    @patch('logging.error')
    def test_logentry_error_level(self, mock_error):
        """
        Test Logger.logentry() with ERROR logging level.
        :returns: Does not return a value.
        """
        test_message = "This is an error message"
        Logger.logentry(test_message, LoggingLevel.ERROR)

        mock_error.assert_called_once_with(test_message)

    @patch('logging.critical')
    def test_logentry_critical_level(self, mock_critical):
        """
        Test Logger.logentry() with CRITICAL logging level.
        :returns: Does not return a value.
        """
        test_message = "This is a critical message"
        Logger.logentry(test_message, LoggingLevel.CRITICAL)

        mock_critical.assert_called_once_with(test_message)

    @patch('logging.debug')
    def test_logentry_debug_level(self, mock_debug):
        """
        Test Logger.logentry() with DEBUG logging level (default case).
        :returns: Does not return a value.
        """
        test_message = "This is a debug message"
        Logger.logentry(test_message, LoggingLevel.DEBUG)

        mock_debug.assert_called_once_with(test_message)

    @patch('logging.debug')
    def test_logentry_unknown_level_defaults_to_debug(self, mock_debug):
        """
        Test Logger.logentry() with unknown logging level defaults to DEBUG.
        :returns: Does not return a value.
        """
        test_message = "This is a message with unknown level"
        # Create a mock LoggingLevel that doesn't match any condition
        mock_level = MagicMock()
        mock_level.__eq__ = MagicMock(return_value=False)

        Logger.logentry(test_message, mock_level)

        mock_debug.assert_called_once_with(test_message)

    def test_static_method_behavior(self):
        """
        Test that Logger methods are static and can be called without instantiation.
        :returns: Does not return a value.
        """
        # Should be able to call static methods without creating instance
        result = Logger.set_configuration(LoggingMode.CONSOLE)
        self.assertEqual(result, str(), "Static method should work without instantiation.")

        # Test logentry as static method
        with patch('logging.info') as mock_info:
            Logger.logentry("Static test", LoggingLevel.INFO)
            mock_info.assert_called_once_with("Static test")

    def test_log_file_naming_uniqueness(self):
        """
        Test that log files have unique names when created multiple times.
        :returns: Does not return a value.
        """
        # Create first log file
        result1 = Logger.set_configuration(LoggingMode.FILE, self.temp_dir)
        logging.getLogger().handlers.clear()

        # Create second log file (should have different timestamp)
        import time
        time.sleep(1)  # Ensure different timestamp
        result2 = Logger.set_configuration(LoggingMode.FILE, self.temp_dir)

        self.assertNotEqual(result1, result2, "Log files should have unique names.")
        self.assertTrue(os.path.exists(result1), "First log file should exist.")
        self.assertTrue(os.path.exists(result2), "Second log file should exist.")

    def test_log_file_content_writing(self):
        """
        Test that log messages are actually written to log files.
        :returns: Does not return a value.
        """
        log_file_path = Logger.set_configuration(LoggingMode.FILE, self.temp_dir)

        test_message = "Test log message for file writing"
        Logger.logentry(test_message, LoggingLevel.INFO)

        # Force logging to flush
        logging.shutdown()

        # Check if file contains the message
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(test_message, content, "Log file should contain the logged message.")
            self.assertIn("INFO", content, "Log file should contain the log level.")

    def test_logging_format_consistency(self):
        """
        Test that logging format is consistent between console and file modes.
        :returns: Does not return a value.
        """
        # Test console mode format
        Logger.set_configuration(LoggingMode.CONSOLE)
        logger = logging.getLogger()
        console_formatter = None
        for handler in logger.handlers:
            if handler.formatter:
                console_formatter = handler.formatter
                break

        logging.getLogger().handlers.clear()

        # Test file mode format
        log_file_path = Logger.set_configuration(LoggingMode.FILE, self.temp_dir)
        logger = logging.getLogger()
        file_formatter = None
        for handler in logger.handlers:
            if handler.formatter:
                file_formatter = handler.formatter
                break

        # Both should have formatters configured
        self.assertIsNotNone(console_formatter, "Console mode should have formatter.")
        self.assertIsNotNone(file_formatter, "File mode should have formatter.")


if __name__ == "__main__":
    unittest.main()
