import base64
import io
import json
import unittest
from email.message import Message
from typing import cast
from unittest.mock import patch

from EMLMailReader import (
    AddressGroup,
    AddressList,
    ContentDisposition,
    DiagnosticSeverity,
    ExternalBodyAccessInfo,
    HeaderCollection,
    HeaderField,
    MailReader,
    MessagePartialInfo,
    ParsedDateTime,
    ParseDiagnostic,
    ParsedMessageID,
    ParserLimits,
    ParsingMode,
    ResentBlock,
    RxMailMessage,
    StandardsComplianceError,
    SyntaxStatus,
    TextEncoding,
    TraceBlock,
    TransferEncoding,
    TransferEncodingValue,
)
from EMLMailReader.RFC_Parser import StandardsParser


class StandardsComplianceTests(unittest.TestCase):
    REQUIRED = (
        b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
        b"From: Alice <alice@example.com>\r\n"
        b"Message-ID: <one@example.com>\r\n"
    )

    def parse(
        self,
        headers: bytes = b"",
        body: bytes = b"",
        *,
        mode: ParsingMode | str = ParsingMode.MODERN,
        limits: ParserLimits | None = None,
    ) -> RxMailMessage:
        source = self.REQUIRED + headers + b"\r\n" + body
        return MailReader(parsing_mode=mode, limits=limits).parse_bytes(source)

    def diagnostic_codes(self, message: RxMailMessage) -> set[str]:
        return {item.code for item in message.Diagnostics}

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

        self.assertEqual(MessagePartialInfo("part", 1, 2).to_dict()["total"], 2)
        self.assertEqual(
            ExternalBodyAccessInfo("URL", {"url": "https://example.com"}).to_dict()[
                "access_type"
            ],
            "URL",
        )
        self.assertEqual(ResentBlock(HeaderCollection()).to_dict(), [])
        self.assertEqual(
            TraceBlock("<sender@example.com>", ["by mx.example.com"]).to_dict()[
                "received"
            ],
            ["by mx.example.com"],
        )

    def test_rfc5322_defaults_and_lossless_source(self) -> None:
        message = self.parse(b"Subject: hello\r\n", b"body\r\n")
        self.assertFalse(message.ContentType.IsExplicit)
        self.assertEqual(message.ContentType.MediaType, "text/plain")
        self.assertEqual(message.ContentType.Charset, "us-ascii")
        self.assertEqual(message.Body, "body")
        self.assertEqual(message.RawBody, b"body\r\n")
        self.assertTrue(message.RawSource.endswith(b"body\r\n"))

    def test_bytes_string_and_stream_entry_points(self) -> None:
        text = self.REQUIRED.decode("ascii") + "Subject: stream\r\n\r\nbody"
        reader = MailReader()
        self.assertEqual(reader.parse_string(text).Subject, "stream")
        self.assertEqual(reader.parse_stream(io.BytesIO(text.encode())).Body, "body")
        stream_message = reader.parse_stream(io.StringIO(text))
        assert stream_message.MessageID is not None
        self.assertEqual(stream_message.MessageID.value, "one@example.com")

    def test_invalid_mode_falls_back_to_modern(self) -> None:
        self.assertEqual(
            StandardsParser("unsupported").parsing_mode, ParsingMode.MODERN
        )

    def test_ordered_duplicate_headers_and_folding(self) -> None:
        message = self.parse(
            b"Received: first\r\n"
            b"Received: second\r\n"
            b"X-Note: one\r\n"
            b" two\r\n"
            b"X-Repeat: old\r\n"
            b"X-Repeat: new\r\n"
        )
        self.assertEqual(message.Headers.get_all("received"), ["first", "second"])
        self.assertEqual(message.Headers.get("X-Note"), "one two")
        self.assertIn("\r\n two", message.Headers.occurrences("X-Note")[0].raw_value)
        self.assertEqual(message.Headers.get("X-Repeat"), "new")

    def test_header_name_matching_is_exact(self) -> None:
        message = self.parse(b"Fromage: cheddar\r\n")
        self.assertEqual(message.From.Mailboxes[0].Email, "alice@example.com")
        self.assertEqual(message.Headers.get("Fromage"), "cheddar")

    def test_structured_mailboxes_groups_and_quoted_commas(self) -> None:
        message = self.parse(
            b'To: Team: "Doe, Jane" <jane@example.com>, bob@example.com;, carol@example.com\r\n'
        )
        self.assertEqual(len(message.To.Mailboxes), 3)
        self.assertIsInstance(message.To.Items[0], AddressGroup)
        group = message.To.Items[0]
        assert isinstance(group, AddressGroup)
        self.assertEqual(group.display_name, "Team")
        self.assertEqual(message.To.Mailboxes[0].DisplayName, "Doe, Jane")
        self.assertIn("Team:", message.To.to_header_value())

    def test_rfc6854_group_from_and_empty_group(self) -> None:
        group = MailReader().parse_bytes(
            b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
            b"From: Authors: a@example.com, b@example.com;\r\n"
            b"Sender: owner@example.com\r\n\r\n"
        )
        self.assertEqual(len(group.From.Mailboxes), 2)
        self.assertNotIn("MissingRequiredSender", self.diagnostic_codes(group))

        empty = MailReader().parse_bytes(
            b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\nFrom: Undisclosed:;\r\n\r\n"
        )
        self.assertEqual(len(empty.From.Mailboxes), 0)
        self.assertNotIn("MissingRequiredFrom", self.diagnostic_codes(empty))

    def test_multiple_from_requires_sender(self) -> None:
        message = MailReader().parse_bytes(
            b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
            b"From: a@example.com, b@example.com\r\n\r\n"
        )
        self.assertIn("MissingRequiredSender", self.diagnostic_codes(message))

    def test_obsolete_receiver_date_is_retained_and_classified(self) -> None:
        message = MailReader().parse_bytes(
            b"Date: 21 Nov 97 09:55:06 GMT\r\nFrom: alice@example.com\r\n\r\n"
        )
        assert message.Date is not None
        self.assertTrue(message.Date.valid)
        self.assertTrue(message.Date.obsolete)

        current = self.parse()
        assert current.Date is not None
        self.assertFalse(current.Date.obsolete)

    def test_obsolete_route_is_accepted_and_classified(self) -> None:
        message = MailReader().parse_bytes(
            b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
            b"From: <@a.example,@b.example:c@example.com>\r\n\r\n"
        )
        self.assertEqual(message.From.Mailboxes[0].Email, "c@example.com")
        self.assertEqual(
            message.Headers.occurrences("From")[0].syntax_status.value, "obsolete"
        )
        self.assertIn("ObsoleteAddressRoute", self.diagnostic_codes(message))

    def test_rfc6532_utf8_headers_addresses_and_message_id(self) -> None:
        source = (
            "Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
            "From: José <josé@例え.テスト>\r\n"
            "To: 李雷 <用户@例子.公司>\r\n"
            "Subject: Привет мир\r\n"
            "Message-ID: <消息@例子.公司>\r\n\r\nbody"
        ).encode()
        message = MailReader().parse_bytes(source)
        self.assertEqual(message.Subject, "Привет мир")
        self.assertEqual(message.From.Mailboxes[0].LocalPart, "josé")
        self.assertTrue(message.From.Mailboxes[0].IsInternationalized)
        assert message.MessageID is not None
        self.assertEqual(message.MessageID.left, "消息")
        self.assertNotIn("InvalidUTF8Header", self.diagnostic_codes(message))

    def test_rfc2047_decodes_multiple_encoded_words_and_mixed_text(self) -> None:
        value = "=?utf-8?Q?Hello_=E2=9C=93?= plain =?iso-8859-1?Q?caf=E9?="
        self.assertEqual(TextEncoding.decode_header(value), "Hello ✓ plain café")
        message = self.parse(f"Subject: {value}\r\n".encode("ascii"))
        self.assertEqual(message.Subject, "Hello ✓ plain café")

    def test_rfc2231_filename_continuations_and_attachment_decoding(self) -> None:
        message = self.parse(
            b"MIME-Version: 1.0\r\n"
            b"Content-Type: application/octet-stream\r\n"
            b"Content-Transfer-Encoding: base64\r\n"
            b"Content-Disposition: attachment;\r\n"
            b" filename*0*=utf-8''%E2%82%AC%20;\r\n"
            b" filename*1*=rates.txt\r\n",
            b"SGVsbG8=\r\n",
        )
        attachment = message.Attachments[0]
        self.assertEqual(attachment.Name, "€ rates.txt")
        self.assertEqual(attachment.DecodedBody, b"Hello")
        assert message.ContentDisposition is not None
        self.assertEqual(message.ContentDisposition.FileName, "€ rates.txt")

    def test_content_disposition_extensions_dates_and_generic_parameters(self) -> None:
        value = (
            "render; filename=report.txt; x-token=yes; size=12; "
            'read-date="Fri, 21 Nov 1997 09:55:06 -0600"'
        )
        disposition = ContentDisposition()
        disposition.parse(value)
        self.assertEqual(disposition.DispositionType, "render")
        self.assertEqual(disposition.get_parameter("x-token"), "yes")
        self.assertEqual(disposition.Size, 12)
        assert disposition.ReadDate is not None
        self.assertIsNotNone(disposition.ReadDate.value)

    def test_binary_and_extension_transfer_encodings_are_not_collapsed(self) -> None:
        binary = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: application/octet-stream\r\n"
            b"Content-Transfer-Encoding: binary\r\n",
            b"data",
        )
        self.assertEqual(binary.ContentTransferEncoding.kind, TransferEncoding.BINARY)
        source = self.REQUIRED + (
            b"MIME-Version: 1.0\r\nContent-Type: application/octet-stream\r\n"
            b"Content-Transfer-Encoding: x-custom\r\n\r\ndata"
        )
        extension = MailReader().parse_bytes(source)
        self.assertEqual(
            extension.ContentTransferEncoding.kind, TransferEncoding.UNKNOWN
        )
        self.assertEqual(extension.ContentTransferEncoding.raw_value, "x-custom")
        self.assertTrue(extension.ContentTransferEncoding.is_extension)

    def test_multipart_hierarchy_preamble_epilogue_and_alternative_bodies(self) -> None:
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=alt\r\n",
            b"preamble\r\n"
            b"--alt\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nplain\r\n"
            b"--alt\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<b>html</b>\r\n"
            b"--alt--\r\nepilogue\r\n",
        )
        self.assertEqual(len(message.Children), 2)
        self.assertEqual(message.Preamble, "preamble")
        self.assertEqual(message.Epilogue, "epilogue\r\n")
        self.assertEqual(message.TextBody, "plain")
        self.assertEqual(message.HtmlBody, "<b>html</b>")
        self.assertEqual(message.Body, "<b>html</b>")

    def test_message_rfc822_is_retained_as_a_nested_message(self) -> None:
        nested = (
            b"Date: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            b"From: Bob <bob@example.com>\r\n"
            b"Subject: nested\r\n\r\ninside"
        )
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/rfc822\r\n",
            nested,
        )
        self.assertEqual(len(message.Children), 1)
        self.assertEqual(message.Children[0].Subject, "nested")
        self.assertEqual(message.Children[0].Body, "inside")

    def test_multipart_digest_uses_message_rfc822_default(self) -> None:
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: multipart/digest; boundary=d\r\n",
            b"--d\r\nDate: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            b"From: bob@example.com\r\nSubject: digest item\r\n\r\ninside\r\n--d--\r\n",
        )
        self.assertEqual(message.Children[0].ContentType.MediaType, "message/rfc822")
        self.assertEqual(message.Children[0].Subject, "digest item")
        self.assertEqual(message.Children[0].Body, "inside")

    def test_message_global_allows_encoded_internationalized_nested_message(
        self,
    ) -> None:
        nested = (
            "Date: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            "From: José <josé@例え.テスト>\r\n"
            "Subject: 世界\r\n\r\ninside"
        ).encode()
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/global\r\n"
            b"Content-Transfer-Encoding: base64\r\n",
            base64.b64encode(nested),
        )
        self.assertNotIn(
            "InvalidCompositeTransferEncoding", self.diagnostic_codes(message)
        )
        self.assertEqual(message.Children[0].Subject, "世界")
        self.assertEqual(message.Children[0].From.Mailboxes[0].LocalPart, "josé")

    def test_message_global_decode_error_is_reported(self) -> None:
        message = self.parse(
            b"MIME-Version: 1.0\r\n"
            b"Content-Type: message/global\r\n"
            b"Content-Transfer-Encoding: quoted-printable\r\n",
            b"not-a-message",
        )
        self.assertTrue(message.Children or message.Diagnostics)

    def test_message_global_decoder_exception_is_diagnostic(self) -> None:
        source = self.REQUIRED + (
            b"MIME-Version: 1.0\r\n"
            b"Content-Type: message/global\r\n"
            b"Content-Transfer-Encoding: base64\r\n\r\n"
            b"RGF0ZTogRnJpLCAyMSBOb3YgMTk5NyAwOTo1NTowNiAtMDYwMA0KDQo="
        )
        with patch(
            "EMLMailReader.RFC_Parser.b64decode",
            side_effect=ValueError("invalid base64"),
        ):
            message = MailReader().parse_bytes(source)
        self.assertIn(
            "InvalidMessageGlobalEncoding",
            self.diagnostic_codes(message),
        )

    def test_message_partial_and_external_body_metadata(self) -> None:
        partial = self.parse(
            b'MIME-Version: 1.0\r\nContent-Type: message/partial; id="part-id"; number=2; total=3\r\n',
            b"fragment",
        )
        assert partial.MessagePartial is not None
        self.assertEqual(partial.MessagePartial.id, "part-id")
        self.assertEqual(partial.MessagePartial.number, 2)
        external = self.parse(
            b'MIME-Version: 1.0\r\nContent-Type: message/external-body; access-type=URL; URL="https://example.com/a"\r\n',
            b"Content-Type: text/plain\r\n\r\n",
        )
        assert external.ExternalBodyAccess is not None
        self.assertEqual(external.ExternalBodyAccess.access_type.lower(), "url")
        self.assertEqual(
            external.ExternalBodyAccess.parameters["url"], "https://example.com/a"
        )

    def test_invalid_message_partial_parameters_are_diagnostic(self) -> None:
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/partial; number=0\r\n",
            b"fragment",
        )
        self.assertIn(
            "InvalidMessagePartialParameters",
            self.diagnostic_codes(message),
        )

    def test_resent_and_trace_blocks_preserve_repeated_fields(self) -> None:
        message = self.parse(
            b"Return-Path: <bounce@example.com>\r\n"
            b"Received: by mx1\r\nReceived: by mx2\r\n"
            b"Resent-Date: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            b"Resent-From: relay@example.com\r\nResent-To: user@example.com\r\n"
        )
        self.assertEqual(len(message.TraceBlocks), 1)
        self.assertEqual(message.TraceBlocks[0].received, ["by mx1", "by mx2"])
        self.assertEqual(len(message.ResentBlocks), 1)
        self.assertEqual(
            message.ResentBlocks[0].fields.get("Resent-To"), "user@example.com"
        )

    def test_resent_and_trace_block_edge_cases(self) -> None:
        message = self.parse(
            b"Resent-Date: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            b"Resent-From: one@example.com, two@example.com\r\n"
            b"Resent-Date: Sun, 23 Nov 1997 10:00:00 -0600\r\n"
            b"Resent-From: relay@example.com\r\n"
            b"Resent-Sender: Team: one@example.com, two@example.com;\r\n"
            b"X-End-Resent: yes\r\n"
            b"Return-Path: <first@example.com>\r\n"
            b"Received: by first.example.com\r\n"
            b"Return-Path: <second@example.com>\r\n"
            b"Received: by second.example.com\r\n",
            b"body",
        )
        codes = self.diagnostic_codes(message)
        self.assertIn("MissingRequiredResentSender", codes)
        self.assertIn("InvalidResentSenderGroup", codes)
        self.assertEqual(len(message.ResentBlocks), 2)
        self.assertEqual(len(message.TraceBlocks), 2)

    def test_cardinality_mime_and_line_diagnostics(self) -> None:
        message = self.parse(
            b"Subject: first\r\nSubject: second\r\nContent-Type: multipart/mixed\r\n",
            b"x" * 999,
        )
        codes = self.diagnostic_codes(message)
        self.assertIn("DuplicateSingletonHeader", codes)
        self.assertIn("MissingMultipartBoundary", codes)
        self.assertIn("MissingMIMEVersion", codes)
        self.assertIn("LineTooLong", codes)

    def test_less_common_mime_validation_paths(self) -> None:
        too_long_boundary = "x" * 71
        boundary = self.parse(
            f"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary={too_long_boundary}\r\n".encode(),
        )
        self.assertIn("MultipartBoundaryTooLong", self.diagnostic_codes(boundary))

        partial = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/partial; id=x; number=2; total=1\r\n"
        )
        self.assertIn("InvalidMessagePartialTotal", self.diagnostic_codes(partial))

        external = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/external-body\r\n"
        )
        self.assertIn("MissingExternalBodyAccessType", self.diagnostic_codes(external))

        composite = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/rfc822\r\n"
            b"Content-Transfer-Encoding: base64\r\n",
            b"broken",
        )
        self.assertIn(
            "InvalidCompositeTransferEncoding", self.diagnostic_codes(composite)
        )

    def test_invalid_imf_and_resent_cardinality_diagnostics(self) -> None:
        message = MailReader().parse_bytes(
            b"Date: never\r\nFrom: a@example.com\r\n"
            b"Sender: Group: a@example.com, b@example.com;\r\n"
            b"Message-ID: not-an-id\r\n"
            b"Resent-To: user@example.com\r\n\r\n"
        )
        codes = self.diagnostic_codes(message)
        self.assertIn("InvalidDate", codes)
        self.assertIn("InvalidMessageID", codes)
        self.assertIn("InvalidSenderGroup", codes)
        self.assertIn("IncompleteResentBlock", codes)

        invalid_mime = self.parse(b"MIME-Version: one\r\nContent-Type: text/plain\r\n")
        self.assertIn("InvalidMIMEVersion", self.diagnostic_codes(invalid_mime))

    def test_unsupported_mime_version_is_warning(self) -> None:
        message = self.parse(
            b"MIME-Version: 2.0\r\nContent-Type: text/plain\r\n",
            b"body",
        )
        self.assertIn("UnsupportedMIMEVersion", self.diagnostic_codes(message))

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
            message = self.parse(b"To: recipient@example.com\r\n", b"body")
        self.assertIn("InvalidAddressList", self.diagnostic_codes(message))

    def test_recursive_resource_limits(self) -> None:
        source = self.REQUIRED + (
            b"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=x\r\n\r\n"
            b"--x\r\nContent-Type: text/plain\r\n\r\none\r\n"
            b"--x\r\nContent-Type: text/plain\r\n\r\ntwo\r\n--x--\r\n"
        )
        limited = MailReader(limits=ParserLimits(max_parts=2)).parse_bytes(source)
        self.assertIn("MimePartLimitExceeded", self.diagnostic_codes(limited))

        depth_limited = MailReader(limits=ParserLimits(max_mime_depth=0)).parse_bytes(
            source
        )
        child_codes = {
            item.code for child in depth_limited.Children for item in child.Diagnostics
        }
        self.assertIn("MimeDepthLimitExceeded", child_codes)

    def test_root_part_count_limit_is_diagnostic(self) -> None:
        message = self.parse(limits=ParserLimits(max_parts=0), body=b"body")
        self.assertIn("MimePartLimitExceeded", self.diagnostic_codes(message))

    def test_payload_and_header_resource_limits_are_diagnostic(self) -> None:
        limits = ParserLimits(
            max_header_bytes=10,
            max_header_count=1,
            max_decoded_part_bytes=2,
        )
        message = self.parse(limits=limits, body=b"body")
        codes = self.diagnostic_codes(message)
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
        self.assertIn("DecodedPartLimitExceeded", self.diagnostic_codes(result))

    def test_modern_mode_reports_implicit_ascii_violation_but_retains_bytes(
        self,
    ) -> None:
        source = self.REQUIRED + b"\r\n\xc3\xa9"
        message = MailReader().parse_bytes(source)
        self.assertEqual(message.DecodedBody, b"\xc3\xa9")
        self.assertIn("InvalidCharsetData", self.diagnostic_codes(message))

    def test_unknown_charset_and_invalid_payload_are_diagnostic(self) -> None:
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: text/plain; charset=x-unknown\r\n",
            b"\xff",
        )
        self.assertEqual(message.Body, "�")
        self.assertIn("InvalidCharsetData", self.diagnostic_codes(message))

    def test_receiver_mode_reports_bare_lf_and_invalid_utf8(self) -> None:
        source = b"Date: Fri, 21 Nov 1997 09:55:06 -0600\nFrom: a@example.com\nX-Bad: \xff\n\nbody"
        message = MailReader().parse_bytes(source)
        codes = self.diagnostic_codes(message)
        self.assertIn("ObsoleteLineEnding", codes)
        self.assertIn("InvalidUTF8Header", codes)

    def test_strict_mode_raises_with_diagnostics(self) -> None:
        with self.assertRaises(StandardsComplianceError) as context:
            MailReader(parsing_mode=ParsingMode.STRICT).parse_bytes(
                b"From: a@example.com\r\n\r\nbody"
            )
        self.assertIn(
            "MissingRequiredDate", {item.code for item in context.exception.diagnostics}
        )

    def test_parser_limits_are_diagnostic_and_strictly_enforceable(self) -> None:
        limits = ParserLimits(max_message_bytes=20)
        message = self.parse(limits=limits)
        self.assertIn("MessageSizeLimitExceeded", self.diagnostic_codes(message))

    def test_json_exposes_the_single_structured_schema(self) -> None:
        message = self.parse(b"Subject: hello\r\n")
        exported = json.loads(message.export_as_json())
        self.assertEqual(exported["schema_version"], 2)
        self.assertEqual(exported["subject"], "hello")
        self.assertIsInstance(exported["headers"], list)

        invalid = MailReader().parse_bytes(b"From: a@example.com\r\n\r\n")
        invalid_json = json.loads(invalid.export_as_json())
        self.assertIn(
            "error", {item["severity"] for item in invalid_json["diagnostics"]}
        )

    def test_attachment_name_uses_content_disposition_precedence(self) -> None:
        source = self.REQUIRED + (
            b"MIME-Version: 1.0\r\n"
            b'Content-Type: application/octet-stream; name="legacy.bin"\r\n'
            b'Content-Disposition: attachment; filename="modern.bin"\r\n\r\ndata'
        )
        attachment = MailReader().parse_bytes(source).Attachments[0]
        self.assertEqual(attachment.Name, "modern.bin")


if __name__ == "__main__":
    unittest.main()
