import io
import unittest
from unittest.mock import patch

from EMLMailReader import (
    LoggingMode,
    MailReader,
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


if __name__ == "__main__":
    unittest.main()
