import unittest
from email.message import Message
from typing import cast
from unittest.mock import patch

from EMLMailReader import (
    AddressList,
    DiagnosticSeverity,
    HeaderCollection,
    HeaderField,
    MailReader,
    ParsedDateTime,
    ParseDiagnostic,
    ParsedMessageID,
    ParserLimits,
    ParsingMode,
    RxMailMessage,
    SyntaxStatus,
    TransferEncoding,
    TransferEncodingValue,
)
from EMLMailReader.RFC_Parser import StandardsParser


class TestVersionTwoCoveragePaths(unittest.TestCase):
    REQUIRED = b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\nFrom: alice@example.com\r\n"

    def test_header_collection_protocol_and_raw_lookup(self) -> None:
        field = HeaderField(
            name="X-Test",
            raw_name="X-Test",
            raw_value=" raw",
            unfolded_value="raw",
            decoded_value="decoded",
            index=0,
            syntax_status=SyntaxStatus.CURRENT,
        )
        headers = HeaderCollection([field])
        self.assertEqual(len(headers), 1)
        self.assertIs(headers[0], field)
        self.assertEqual(list(headers), [field])
        self.assertEqual(headers.get("x-test"), "decoded")
        self.assertEqual(headers.get("x-test", decoded=False), "raw")
        self.assertEqual(headers.get("missing", "fallback"), "fallback")
        self.assertEqual(headers.occurrences("X-TEST"), [field])
        self.assertEqual(headers.to_list()[0]["syntax_status"], "current")

    def test_structured_values_export(self) -> None:
        message_id = ParsedMessageID(
            "<a@example.com>", "a@example.com", "a", "example.com"
        )
        self.assertEqual(message_id.to_dict()["left"], "a")

        parsed_date = ParsedDateTime("raw", None, False)
        self.assertIsNone(parsed_date.to_dict()["value"])

        diagnostic = ParseDiagnostic(
            "Example",
            "message",
            DiagnosticSeverity.INFO,
            rfc="RFC 5322",
        )
        self.assertEqual(diagnostic.to_dict()["severity"], "info")

        transfer = TransferEncodingValue.parse("")
        self.assertEqual(transfer.kind, TransferEncoding.SEVEN_BIT)

    def test_invalid_mode_falls_back_to_modern(self) -> None:
        self.assertEqual(
            StandardsParser("unsupported").parsing_mode, ParsingMode.MODERN
        )

    def test_unknown_charset_and_invalid_payload_are_diagnostic(self) -> None:
        message = MailReader().parse_bytes(
            self.REQUIRED
            + b"MIME-Version: 1.0\r\n"
            + b"Content-Type: text/plain; charset=x-unknown\r\n\r\n"
            + b"\xff"
        )
        self.assertEqual(message.Body, "�")
        self.assertIn("InvalidCharsetData", {item.code for item in message.Diagnostics})

    def test_unsupported_mime_version_is_warning(self) -> None:
        message = MailReader().parse_bytes(
            self.REQUIRED + b"MIME-Version: 2.0\r\nContent-Type: text/plain\r\n\r\nbody"
        )
        self.assertIn(
            "UnsupportedMIMEVersion", {item.code for item in message.Diagnostics}
        )

    def test_message_global_decode_error_is_reported(self) -> None:
        message = MailReader().parse_bytes(
            self.REQUIRED
            + b"MIME-Version: 1.0\r\n"
            + b"Content-Type: message/global\r\n"
            + b"Content-Transfer-Encoding: quoted-printable\r\n\r\n"
            + b"not-a-message"
        )
        self.assertTrue(message.Children or message.Diagnostics)

    def test_message_global_decoder_exception_is_diagnostic(self) -> None:
        source = (
            self.REQUIRED
            + b"MIME-Version: 1.0\r\n"
            + b"Content-Type: message/global\r\n"
            + b"Content-Transfer-Encoding: base64\r\n\r\n"
            + b"RGF0ZTogRnJpLCAyMSBOb3YgMTk5NyAwOTo1NTowNiAtMDYwMA0KDQo="
        )
        with patch(
            "EMLMailReader.RFC_Parser.b64decode",
            side_effect=ValueError("invalid base64"),
        ):
            message = MailReader().parse_bytes(source)
        self.assertIn(
            "InvalidMessageGlobalEncoding",
            {item.code for item in message.Diagnostics},
        )

    def test_invalid_address_list_is_retained_as_a_diagnostic(self) -> None:
        real_address_list = AddressList
        failed = False

        def parse_address_list(raw_value: str = "") -> AddressList:
            nonlocal failed
            if raw_value and not failed:
                failed = True
                raise ValueError("invalid address list")
            return real_address_list(raw_value)

        with patch(
            "EMLMailReader.RFC_Parser.AddressList",
            side_effect=parse_address_list,
        ):
            message = MailReader().parse_bytes(
                self.REQUIRED + b"To: recipient@example.com\r\n\r\nbody"
            )
        self.assertIn("InvalidAddressList", {item.code for item in message.Diagnostics})

    def test_root_part_count_limit_is_diagnostic(self) -> None:
        message = MailReader(limits=ParserLimits(max_parts=0)).parse_bytes(
            self.REQUIRED + b"\r\nbody"
        )
        self.assertIn(
            "MimePartLimitExceeded", {item.code for item in message.Diagnostics}
        )

    def test_payload_and_header_resource_limits_are_diagnostic(self) -> None:
        limits = ParserLimits(
            max_header_bytes=10,
            max_header_count=1,
            max_decoded_part_bytes=2,
        )
        message = MailReader(limits=limits).parse_bytes(self.REQUIRED + b"\r\nbody")
        codes = {item.code for item in message.Diagnostics}
        self.assertIn("HeaderSizeLimitExceeded", codes)
        self.assertIn("HeaderCountLimitExceeded", codes)
        self.assertIn("DecodedPartLimitExceeded", codes)

    def test_leaf_payload_none_uses_string_fallback(self) -> None:
        class PayloadWithoutDecodedBytes:
            @staticmethod
            def get_payload(decode: bool = False) -> str | None:
                return None if decode else "fallback"

            @staticmethod
            def get_content_type() -> str:
                return "application/octet-stream"

        result = RxMailMessage()
        parser = StandardsParser(limits=ParserLimits(max_decoded_part_bytes=2))
        parser._populate_leaf_body(
            result,
            cast(Message, PayloadWithoutDecodedBytes()),
        )
        self.assertEqual(result.DecodedBody, b"fallback")
        self.assertIn(
            "DecodedPartLimitExceeded",
            {item.code for item in result.Diagnostics},
        )

    def test_invalid_message_partial_parameters_are_diagnostic(self) -> None:
        message = MailReader().parse_bytes(
            self.REQUIRED
            + b"MIME-Version: 1.0\r\n"
            + b"Content-Type: message/partial; number=0\r\n\r\nfragment"
        )
        self.assertIn(
            "InvalidMessagePartialParameters",
            {item.code for item in message.Diagnostics},
        )

    def test_resent_and_trace_block_edge_cases(self) -> None:
        message = MailReader().parse_bytes(
            self.REQUIRED
            + b"Resent-Date: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            + b"Resent-From: one@example.com, two@example.com\r\n"
            + b"Resent-Date: Sun, 23 Nov 1997 10:00:00 -0600\r\n"
            + b"Resent-From: relay@example.com\r\n"
            + b"Resent-Sender: Team: one@example.com, two@example.com;\r\n"
            + b"X-End-Resent: yes\r\n"
            + b"Return-Path: <first@example.com>\r\n"
            + b"Received: by first.example.com\r\n"
            + b"Return-Path: <second@example.com>\r\n"
            + b"Received: by second.example.com\r\n\r\nbody"
        )
        codes = {item.code for item in message.Diagnostics}
        self.assertIn("MissingRequiredResentSender", codes)
        self.assertIn("InvalidResentSenderGroup", codes)
        self.assertEqual(len(message.ResentBlocks), 2)
        self.assertEqual(len(message.TraceBlocks), 2)

    def test_logger_receives_non_error_diagnostics_as_info(self) -> None:
        with patch("EMLMailReader.Mail_Reader.Logger.logentry") as logentry:
            MailReader().parse_bytes(
                self.REQUIRED + b"Content-Type: text/plain\r\n\r\nbody"
            )
        self.assertTrue(logentry.called)


if __name__ == "__main__":
    unittest.main()
