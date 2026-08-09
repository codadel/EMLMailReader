import io
import unittest
from unittest.mock import mock_open, patch

from EMLMailReader import (
    DiagnosticSeverity,
    LoggingMode,
    MailReader,
    ParseDiagnostic,
    StandardsComplianceError,
)


class TestMailReader(unittest.TestCase):
    SOURCE = (
        b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
        b"From: Alice <alice@example.com>\r\n"
        b"Subject: hello\r\n\r\nbody"
    )

    def test_bytes_string_and_stream_entry_points(self) -> None:
        reader = MailReader()
        self.assertEqual(reader.parse_bytes(self.SOURCE).Subject, "hello")
        self.assertEqual(reader.parse_string(self.SOURCE.decode()).Body, "body")
        self.assertEqual(reader.parse_stream(io.BytesIO(self.SOURCE)).Body, "body")
        self.assertEqual(
            reader.parse_stream(io.StringIO(self.SOURCE.decode())).Body, "body"
        )

    def test_constructor_configures_requested_logging_mode(self) -> None:
        with patch("EMLMailReader.Mail_Reader.Logger.set_configuration") as configure:
            MailReader(logging_mode=LoggingMode.CONSOLE)
            configure.assert_called_once_with(LoggingMode.CONSOLE)

        with patch("EMLMailReader.Mail_Reader.Logger.set_configuration") as configure:
            MailReader(logging_mode=LoggingMode.FILE, TargetLoggingFolder="/logs")
            configure.assert_called_once_with(LoggingMode.FILE, "/logs")

    def test_nested_diagnostics_are_logged(self) -> None:
        source = (
            self.SOURCE.split(b"\r\n\r\n")[0]
            + b"\r\nMIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=x\r\n\r\n"
            + b"--x\r\nContent-Type: text/plain\r\nContent-Type: text/html\r\n\r\nbody\r\n--x--\r\n"
        )
        with patch("EMLMailReader.Mail_Reader.Logger.logentry") as logentry:
            MailReader().parse_bytes(source)
        self.assertTrue(
            any(
                "DuplicateMIMEHeader" in call.args[0]
                for call in logentry.call_args_list
            )
        )

    def test_non_error_diagnostics_are_logged_as_info(self) -> None:
        source = (
            self.SOURCE.split(b"\r\n\r\n")[0]
            + b"\r\nContent-Type: text/plain\r\n\r\nbody"
        )
        with patch("EMLMailReader.Mail_Reader.Logger.logentry") as logentry:
            MailReader().parse_bytes(source)
        self.assertTrue(logentry.called)

    def test_get_email_handles_file_outcomes_without_real_files(self) -> None:
        with (
            patch("EMLMailReader.Mail_Reader.os.path.exists", return_value=False),
            patch("EMLMailReader.Mail_Reader.Logger.logentry") as logentry,
        ):
            self.assertIsNone(MailReader().get_email("missing.eml"))
        self.assertTrue(logentry.called)

        empty_file = mock_open(read_data=b"")
        with (
            patch("EMLMailReader.Mail_Reader.os.path.exists", return_value=True),
            patch("builtins.open", empty_file),
        ):
            self.assertIsNone(MailReader().get_email("empty.eml"))
        empty_file().close.assert_called_once_with()

        source_file = mock_open(read_data=self.SOURCE)
        with (
            patch("EMLMailReader.Mail_Reader.os.path.exists", return_value=True),
            patch("builtins.open", source_file),
        ):
            message = MailReader().get_email("message.eml")
        self.assertIsNotNone(message)
        assert message is not None
        self.assertEqual(message.Subject, "hello")
        source_file().close.assert_called_once_with()

        unreadable_file = mock_open()
        unreadable_file().read.side_effect = OSError("unreadable")
        with (
            patch("EMLMailReader.Mail_Reader.os.path.exists", return_value=True),
            patch("builtins.open", unreadable_file),
            patch("EMLMailReader.Mail_Reader.Logger.logentry") as logentry,
        ):
            self.assertIsNone(MailReader().get_email("unreadable.eml"))
        unreadable_file().close.assert_called_once_with()
        self.assertTrue(logentry.called)

    def test_get_email_propagates_strict_compliance_errors(self) -> None:
        error = StandardsComplianceError(
            [
                ParseDiagnostic(
                    code="ExampleError",
                    message="invalid message",
                    severity=DiagnosticSeverity.ERROR,
                )
            ]
        )
        source_file = mock_open(read_data=self.SOURCE)
        reader = MailReader()
        with (
            patch("EMLMailReader.Mail_Reader.os.path.exists", return_value=True),
            patch("builtins.open", source_file),
            patch.object(reader, "parse_bytes", side_effect=error),
            self.assertRaises(StandardsComplianceError),
        ):
            reader.get_email("strict.eml")
        source_file().close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
