import unittest
import logging
from unittest.mock import patch, MagicMock
from EMLMailReader import Logger, LoggingMode
from EMLMailReader.Enumerations import LoggingLevel


class TestProcessingLogs(unittest.TestCase):
    """
    A unit test case to check the Logger class methods exposed by the EMLMailReader library.
    """

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

if __name__ == "__main__":
    unittest.main()
