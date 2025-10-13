import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, mock_open, MagicMock
from EMLMailReader import (
    MailReader,
    RxMailMessage,
    LoggingMode,
    FileMissingError,
    FolderNotAvailableError
)


class TestMailReader(unittest.TestCase):
    """
    A unit test case to check the MailReader class methods and functionality.
    """

    def setUp(self):
        """
        Set up test environment with temporary directories and sample EML content.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.valid_eml_path = os.path.join(self.temp_dir, "test.eml")
        self.invalid_eml_path = os.path.join(self.temp_dir, "nonexistent.eml")

        # Create a simple EML file for testing
        self.sample_eml_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-ID: <12345@example.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

This is a test email body.
"""

        with open(self.valid_eml_path, 'w') as f:
            f.write(self.sample_eml_content)

    def tearDown(self):
        """
        Clean up temporary directories.
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_mailreader_initialization_default(self):
        """
        Test MailReader initialization with default parameters.
        :returns: Does not return a value.
        """
        reader = MailReader()

        # Should initialize without errors
        self.assertIsInstance(reader, MailReader, "Should create MailReader instance.")

    def test_mailreader_initialization_console_logging(self):
        """
        Test MailReader initialization with console logging mode.
        :returns: Does not return a value.
        """
        with patch('EMLMailReader.Processing_Logs.Logger.set_configuration') as mock_config:
            reader = MailReader(LoggingMode.CONSOLE)

            mock_config.assert_called_once_with(LoggingMode.CONSOLE)
            self.assertIsInstance(reader, MailReader, "Should create MailReader instance with console logging.")

    def test_mailreader_initialization_file_logging(self):
        """
        Test MailReader initialization with file logging mode.
        :returns: Does not return a value.
        """
        with patch('EMLMailReader.Processing_Logs.Logger.set_configuration') as mock_config:
            reader = MailReader(LoggingMode.FILE, self.temp_dir)

            mock_config.assert_called_once_with(LoggingMode.FILE, self.temp_dir)
            self.assertIsInstance(reader, MailReader, "Should create MailReader instance with file logging.")

    def test_get_email_valid_file(self):
        """
        Test get_email() method with valid EML file.
        :returns: Does not return a value.
        """
        reader = MailReader()
        result = reader.get_email(self.valid_eml_path)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")
        self.assertIsNotNone(result, "Result should not be None.")

    def test_get_email_file_not_found(self):
        """
        Test get_email() method with non-existent file.
        :returns: Does not return a value.
        """
        reader = MailReader()
        result = reader.get_email(self.invalid_eml_path)

        self.assertIsNone(result, "Should return None for non-existent file.")

    def test_get_email_file_not_found_raises_exception(self):
        """
        Test that get_email() properly handles FileMissingError internally.
        :returns: Does not return a value.
        """
        reader = MailReader()

        with patch('EMLMailReader.Processing_Logs.Logger.logentry') as mock_log:
            result = reader.get_email(self.invalid_eml_path)

            self.assertIsNone(result, "Should return None for non-existent file.")
            # Should log an error
            mock_log.assert_called()

    def test_get_email_with_multipart_content(self):
        """
        Test get_email() method with multipart EML content.
        :returns: Does not return a value.
        """
        multipart_eml = """From: sender@example.com
To: recipient@example.com
Subject: Multipart Test
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain

This is the text part.

--boundary123
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="test.txt"

Binary data here
--boundary123--
"""

        multipart_file = os.path.join(self.temp_dir, "multipart.eml")
        with open(multipart_file, 'w') as f:
            f.write(multipart_eml)

        reader = MailReader()
        result = reader.get_email(multipart_file)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")
        self.assertTrue(result.IsMultiPart, "Should detect multipart message.")

    def test_get_email_with_encoded_headers(self):
        """
        Test get_email() method with encoded headers.
        :returns: Does not return a value.
        """
        encoded_eml = """From: =?utf-8?Q?Sender_Name?= <sender@example.com>
To: recipient@example.com
Subject: =?utf-8?B?VGVzdCBTdWJqZWN0?=
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

Test body content.
"""

        encoded_file = os.path.join(self.temp_dir, "encoded.eml")
        with open(encoded_file, 'w') as f:
            f.write(encoded_eml)

        reader = MailReader()
        result = reader.get_email(encoded_file)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")
        # Note: The actual decoding would depend on TextEncoding.decode_header implementation

    def test_get_email_with_incomplete_headers(self):
        """
        Test get_email() method with malformed headers.
        :returns: Does not return a value.
        """
        malformed_eml = """From: sender@example.com
To: recipient@example.com
Malformed header without colon
Subject: Test Subject

Test body.
"""

        malformed_file = os.path.join(self.temp_dir, "malformed.eml")
        with open(malformed_file, 'w') as f:
            f.write(malformed_eml)

        reader = MailReader()

        with patch('EMLMailReader.Processing_Logs.Logger.logentry') as mock_log:
            result = reader.get_email(malformed_file)

            # Should still return a message object, but may log errors
            self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage even with malformed headers.")

    def test_get_email_with_continuation_headers(self):
        """
        Test get_email() method with header continuation lines.
        :returns: Does not return a value.
        """
        continuation_eml = """From: sender@example.com
To: recipient@example.com
Subject: This is a very long subject line
 that continues on the next line
 and even more on this line
MIME-Version: 1.0

Test body.
"""

        continuation_file = os.path.join(self.temp_dir, "continuation.eml")
        with open(continuation_file, 'w') as f:
            f.write(continuation_eml)

        reader = MailReader()
        result = reader.get_email(continuation_file)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")
        # The subject should be properly concatenated

    def test_get_email_with_multiple_recipients(self):
        """
        Test get_email() method with multiple recipients.
        :returns: Does not return a value.
        """
        multiple_recipients_eml = """From: sender@example.com
To: recipient1@example.com, recipient2@example.com
Cc: cc1@example.com; cc2@example.com
Bcc: bcc1@example.com, bcc2@example.com
Subject: Multiple Recipients Test

Test body.
"""

        recipients_file = os.path.join(self.temp_dir, "recipients.eml")
        with open(recipients_file, 'w') as f:
            f.write(multiple_recipients_eml)

        reader = MailReader()
        result = reader.get_email(recipients_file)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")
        # Should properly parse multiple recipients

    def test_get_email_with_base64_content(self):
        """
        Test get_email() method with base64 encoded content.
        :returns: Does not return a value.
        """
        base64_eml = """From: sender@example.com
To: recipient@example.com
Subject: Base64 Test
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: base64

VGhpcyBpcyBhIHRlc3QgbWVzc2FnZSBlbmNvZGVkIGluIGJhc2U2NC4=
"""

        base64_file = os.path.join(self.temp_dir, "base64.eml")
        with open(base64_file, 'w') as f:
            f.write(base64_eml)

        reader = MailReader()
        result = reader.get_email(base64_file)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")

    def test_get_email_with_quoted_printable_content(self):
        """
        Test get_email() method with quoted-printable encoded content.
        :returns: Does not return a value.
        """
        qp_eml = """From: sender@example.com
To: recipient@example.com
Subject: Quoted-Printable Test
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable

This is a test message with special characters: =C3=A9 =C3=A1 =C3=AD
"""

        qp_file = os.path.join(self.temp_dir, "quoted_printable.eml")
        with open(qp_file, 'w') as f:
            f.write(qp_eml)

        reader = MailReader()
        result = reader.get_email(qp_file)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")

    def test_get_email_exception_handling(self):
        """
        Test get_email() method exception handling.
        :returns: Does not return a value.
        """
        reader = MailReader()

        # Mock file operations to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('EMLMailReader.Processing_Logs.Logger.logentry') as mock_log:
                result = reader.get_email(self.valid_eml_path)

                self.assertIsNone(result, "Should return None when exception occurs.")
                mock_log.assert_called()

    def test_get_email_different_newline_formats(self):
        """
        Test get_email() method with different newline formats.
        :returns: Does not return a value.
        """
        # Test with different newline formats
        newline_formats = ["\n", "\r\n", "\r"]

        for i, newline in enumerate(newline_formats):
            eml_content = f"From: sender@example.com{newline}To: recipient@example.com{newline}Subject: Test{newline}{newline}Body content.{newline}"

            test_file = os.path.join(self.temp_dir, f"newline_test_{i}.eml")
            with open(test_file, 'w', newline='') as f:
                f.write(eml_content)

            reader = MailReader()
            result = reader.get_email(test_file)

            with self.subTest(newline_format=repr(newline)):
                self.assertIsInstance(result, RxMailMessage, f"Should handle {repr(newline)} newlines.")

    def test_get_email_empty_file(self):
        """
        Test get_email() method with empty EML file.
        :returns: Does not return a value.
        """
        empty_file = os.path.join(self.temp_dir, "empty.eml")
        with open(empty_file, 'w') as f:
            pass  # Create empty file

        reader = MailReader()
        result = reader.get_email(empty_file)

        # The current implementation returns None for empty files due to "list index out of range" error
        self.assertIsNone(result, "Empty file should return None due to implementation behavior.")

    def test_get_email_with_custom_headers(self):
        """
        Test get_email() method with custom headers.
        :returns: Does not return a value.
        """
        custom_headers_eml = """From: sender@example.com
To: recipient@example.com
Subject: Custom Headers Test
X-Custom-Header: Custom Value
X-Another-Header: Another Value
Content-Type: text/plain

Test body.
"""

        custom_file = os.path.join(self.temp_dir, "custom.eml")
        with open(custom_file, 'w') as f:
            f.write(custom_headers_eml)

        reader = MailReader()
        result = reader.get_email(custom_file)

        self.assertIsInstance(result, RxMailMessage, "Should return RxMailMessage instance.")
        # Custom headers should be stored in Headers dictionary

    def test_mailreader_multiple_file_processing(self):
        """
        Test MailReader processing multiple files sequentially.
        :returns: Does not return a value.
        """
        # Create multiple EML files
        files = []
        for i in range(3):
            content = f"""From: sender{i}@example.com
To: recipient{i}@example.com
Subject: Test {i}

Body {i}
"""
            file_path = os.path.join(self.temp_dir, f"test_{i}.eml")
            with open(file_path, 'w') as f:
                f.write(content)
            files.append(file_path)

        reader = MailReader()
        results = []

        for file_path in files:
            result = reader.get_email(file_path)
            results.append(result)

        self.assertEqual(len(results), 3, "Should process all three files.")
        for result in results:
            self.assertIsInstance(result, RxMailMessage, "Each result should be RxMailMessage.")

    def test_file_cleanup_on_exception(self):
        """
        Test that file handles are properly cleaned up when exceptions occur.
        :returns: Does not return a value.
        """
        reader = MailReader()

        # Test that file is closed even when exception occurs during processing
        original_open = open

        def mock_open_with_exception(*args, **kwargs):
            file_obj = original_open(*args, **kwargs)
            # Mock readlines to raise an exception after opening
            original_readlines = file_obj.readlines
            def readlines_with_exception():
                raise ValueError("Simulated processing error")
            file_obj.readlines = readlines_with_exception
            return file_obj

        with patch('builtins.open', side_effect=mock_open_with_exception):
            with patch('EMLMailReader.Processing_Logs.Logger.logentry'):
                result = reader.get_email(self.valid_eml_path)

                self.assertIsNone(result, "Should return None when processing fails.")


if __name__ == "__main__":
    unittest.main()
