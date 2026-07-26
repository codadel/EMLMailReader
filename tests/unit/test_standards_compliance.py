import json
import base64
import io
import unittest

from EMLMailReader import (
    AddressGroup,
    ContentDisposition,
    MailReader,
    ParserLimits,
    ParsingMode,
    StandardsComplianceError,
    TextEncoding,
    TransferEncoding,
)


class StandardsComplianceTests(unittest.TestCase):
    REQUIRED = (
        b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
        b"From: Alice <alice@example.com>\r\n"
        b"Message-ID: <one@example.com>\r\n"
    )

    def parse(self, headers=b"", body=b"", *, mode=ParsingMode.MODERN, limits=None):
        source = self.REQUIRED + headers + b"\r\n" + body
        return MailReader(parsing_mode=mode, limits=limits).parse_bytes(source)

    def diagnostic_codes(self, message):
        return {item.code for item in message.Diagnostics}

    def test_rfc5322_defaults_and_lossless_source(self):
        message = self.parse(b"Subject: hello\r\n", b"body\r\n")
        self.assertFalse(message.ContentType.IsExplicit)
        self.assertEqual(message.ContentType.MediaType, "text/plain")
        self.assertEqual(message.ContentType.Charset, "us-ascii")
        self.assertEqual(message.Body, "body")
        self.assertEqual(message.RawBody, b"body\r\n")
        self.assertTrue(message.RawSource.endswith(b"body\r\n"))

    def test_bytes_string_and_stream_entry_points(self):
        text = self.REQUIRED.decode("ascii") + "Subject: stream\r\n\r\nbody"
        reader = MailReader()
        self.assertEqual(reader.parse_string(text).Subject, "stream")
        self.assertEqual(reader.parse_stream(io.BytesIO(text.encode())).Body, "body")
        self.assertEqual(reader.parse_stream(io.StringIO(text)).MessageID.value, "one@example.com")

    def test_ordered_duplicate_headers_and_folding(self):
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

    def test_header_name_matching_is_exact(self):
        message = self.parse(b"Fromage: cheddar\r\n")
        self.assertEqual(message.From.Mailboxes[0].Email, "alice@example.com")
        self.assertEqual(message.Headers.get("Fromage"), "cheddar")

    def test_structured_mailboxes_groups_and_quoted_commas(self):
        message = self.parse(
            b"To: Team: \"Doe, Jane\" <jane@example.com>, bob@example.com;, carol@example.com\r\n"
        )
        self.assertEqual(len(message.To.Mailboxes), 3)
        self.assertIsInstance(message.To.Items[0], AddressGroup)
        self.assertEqual(message.To.Items[0].display_name, "Team")
        self.assertEqual(message.To.Mailboxes[0].DisplayName, "Doe, Jane")
        self.assertIn("Team:", message.To.to_header_value())

    def test_rfc6854_group_from_and_empty_group(self):
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

    def test_multiple_from_requires_sender(self):
        message = MailReader().parse_bytes(
            b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
            b"From: a@example.com, b@example.com\r\n\r\n"
        )
        self.assertIn("MissingRequiredSender", self.diagnostic_codes(message))

    def test_obsolete_receiver_date_is_retained_and_classified(self):
        message = MailReader().parse_bytes(
            b"Date: 21 Nov 97 09:55:06 GMT\r\nFrom: alice@example.com\r\n\r\n"
        )
        self.assertTrue(message.Date.valid)
        self.assertTrue(message.Date.obsolete)

        current = self.parse()
        self.assertFalse(current.Date.obsolete)

    def test_obsolete_route_is_accepted_and_classified(self):
        message = MailReader().parse_bytes(
            b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
            b"From: <@a.example,@b.example:c@example.com>\r\n\r\n"
        )
        self.assertEqual(message.From.Mailboxes[0].Email, "c@example.com")
        self.assertEqual(message.Headers.occurrences("From")[0].syntax_status.value, "obsolete")
        self.assertIn("ObsoleteAddressRoute", self.diagnostic_codes(message))

    def test_rfc6532_utf8_headers_addresses_and_message_id(self):
        source = (
            "Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
            "From: José <josé@例え.テスト>\r\n"
            "To: 李雷 <用户@例子.公司>\r\n"
            "Subject: Привет мир\r\n"
            "Message-ID: <消息@例子.公司>\r\n\r\nbody"
        ).encode("utf-8")
        message = MailReader().parse_bytes(source)
        self.assertEqual(message.Subject, "Привет мир")
        self.assertEqual(message.From.Mailboxes[0].LocalPart, "josé")
        self.assertTrue(message.From.Mailboxes[0].IsInternationalized)
        self.assertEqual(message.MessageID.left, "消息")
        self.assertNotIn("InvalidUTF8Header", self.diagnostic_codes(message))

    def test_rfc2047_decodes_multiple_encoded_words_and_mixed_text(self):
        value = "=?utf-8?Q?Hello_=E2=9C=93?= plain =?iso-8859-1?Q?caf=E9?="
        self.assertEqual(TextEncoding.decode_header(value), "Hello ✓ plain café")
        message = self.parse(f"Subject: {value}\r\n".encode("ascii"))
        self.assertEqual(message.Subject, "Hello ✓ plain café")

    def test_rfc2231_filename_continuations_and_attachment_decoding(self):
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
        self.assertEqual(message.ContentDisposition.FileName, "€ rates.txt")

    def test_content_disposition_extensions_dates_and_generic_parameters(self):
        value = (
            "render; filename=report.txt; x-token=yes; size=12; "
            'read-date="Fri, 21 Nov 1997 09:55:06 -0600"'
        )
        disposition = ContentDisposition()
        disposition.parse(value)
        self.assertEqual(disposition.DispositionType, "render")
        self.assertEqual(disposition.get_parameter("x-token"), "yes")
        self.assertEqual(disposition.Size, 12)
        self.assertIsNotNone(disposition.ReadDate.value)

    def test_binary_and_extension_transfer_encodings_are_not_collapsed(self):
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
        self.assertEqual(extension.ContentTransferEncoding.kind, TransferEncoding.UNKNOWN)
        self.assertEqual(extension.ContentTransferEncoding.raw_value, "x-custom")
        self.assertTrue(extension.ContentTransferEncoding.is_extension)

    def test_multipart_hierarchy_preamble_epilogue_and_alternative_bodies(self):
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

    def test_message_rfc822_is_retained_as_a_nested_message(self):
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

    def test_multipart_digest_uses_message_rfc822_default(self):
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: multipart/digest; boundary=d\r\n",
            b"--d\r\nDate: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            b"From: bob@example.com\r\nSubject: digest item\r\n\r\ninside\r\n--d--\r\n",
        )
        self.assertEqual(message.Children[0].ContentType.MediaType, "message/rfc822")
        self.assertEqual(message.Children[0].Subject, "digest item")
        self.assertEqual(message.Children[0].Body, "inside")

    def test_message_global_allows_encoded_internationalized_nested_message(self):
        nested = (
            "Date: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            "From: José <josé@例え.テスト>\r\n"
            "Subject: 世界\r\n\r\ninside"
        ).encode("utf-8")
        message = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/global\r\n"
            b"Content-Transfer-Encoding: base64\r\n",
            base64.b64encode(nested),
        )
        self.assertNotIn("InvalidCompositeTransferEncoding", self.diagnostic_codes(message))
        self.assertEqual(message.Children[0].Subject, "世界")
        self.assertEqual(message.Children[0].From.Mailboxes[0].LocalPart, "josé")

    def test_message_partial_and_external_body_metadata(self):
        partial = self.parse(
            b'MIME-Version: 1.0\r\nContent-Type: message/partial; id="part-id"; number=2; total=3\r\n',
            b"fragment",
        )
        self.assertEqual(partial.MessagePartial.id, "part-id")
        self.assertEqual(partial.MessagePartial.number, 2)
        external = self.parse(
            b'MIME-Version: 1.0\r\nContent-Type: message/external-body; access-type=URL; URL="https://example.com/a"\r\n',
            b"Content-Type: text/plain\r\n\r\n",
        )
        self.assertEqual(external.ExternalBodyAccess.access_type.lower(), "url")
        self.assertEqual(external.ExternalBodyAccess.parameters["url"], "https://example.com/a")

    def test_resent_and_trace_blocks_preserve_repeated_fields(self):
        message = self.parse(
            b"Return-Path: <bounce@example.com>\r\n"
            b"Received: by mx1\r\nReceived: by mx2\r\n"
            b"Resent-Date: Sat, 22 Nov 1997 10:00:00 -0600\r\n"
            b"Resent-From: relay@example.com\r\nResent-To: user@example.com\r\n"
        )
        self.assertEqual(len(message.TraceBlocks), 1)
        self.assertEqual(message.TraceBlocks[0].received, ["by mx1", "by mx2"])
        self.assertEqual(len(message.ResentBlocks), 1)
        self.assertEqual(message.ResentBlocks[0].fields.get("Resent-To"), "user@example.com")

    def test_cardinality_mime_and_line_diagnostics(self):
        message = self.parse(
            b"Subject: first\r\nSubject: second\r\n"
            b"Content-Type: multipart/mixed\r\n",
            b"x" * 999,
        )
        codes = self.diagnostic_codes(message)
        self.assertIn("DuplicateSingletonHeader", codes)
        self.assertIn("MissingMultipartBoundary", codes)
        self.assertIn("MissingMIMEVersion", codes)
        self.assertIn("LineTooLong", codes)

    def test_less_common_mime_validation_paths(self):
        too_long_boundary = "x" * 71
        boundary = self.parse(
            f"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary={too_long_boundary}\r\n".encode(),
        )
        self.assertIn("MultipartBoundaryTooLong", self.diagnostic_codes(boundary))

        partial = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/partial; id=x; number=2; total=1\r\n"
        )
        self.assertIn("InvalidMessagePartialTotal", self.diagnostic_codes(partial))

        external = self.parse(b"MIME-Version: 1.0\r\nContent-Type: message/external-body\r\n")
        self.assertIn("MissingExternalBodyAccessType", self.diagnostic_codes(external))

        composite = self.parse(
            b"MIME-Version: 1.0\r\nContent-Type: message/rfc822\r\n"
            b"Content-Transfer-Encoding: base64\r\n",
            b"broken",
        )
        self.assertIn("InvalidCompositeTransferEncoding", self.diagnostic_codes(composite))

    def test_invalid_imf_and_resent_cardinality_diagnostics(self):
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

    def test_recursive_resource_limits(self):
        source = self.REQUIRED + (
            b"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=x\r\n\r\n"
            b"--x\r\nContent-Type: text/plain\r\n\r\none\r\n"
            b"--x\r\nContent-Type: text/plain\r\n\r\ntwo\r\n--x--\r\n"
        )
        limited = MailReader(limits=ParserLimits(max_parts=2)).parse_bytes(source)
        self.assertIn("MimePartLimitExceeded", self.diagnostic_codes(limited))

        depth_limited = MailReader(limits=ParserLimits(max_mime_depth=0)).parse_bytes(source)
        child_codes = {item.code for child in depth_limited.Children for item in child.Diagnostics}
        self.assertIn("MimeDepthLimitExceeded", child_codes)

    def test_modern_mode_reports_implicit_ascii_violation_but_retains_bytes(self):
        source = self.REQUIRED + b"\r\n\xc3\xa9"
        message = MailReader().parse_bytes(source)
        self.assertEqual(message.DecodedBody, b"\xc3\xa9")
        self.assertIn("InvalidCharsetData", self.diagnostic_codes(message))

    def test_receiver_mode_reports_bare_lf_and_invalid_utf8(self):
        source = b"Date: Fri, 21 Nov 1997 09:55:06 -0600\nFrom: a@example.com\nX-Bad: \xff\n\nbody"
        message = MailReader().parse_bytes(source)
        codes = self.diagnostic_codes(message)
        self.assertIn("ObsoleteLineEnding", codes)
        self.assertIn("InvalidUTF8Header", codes)

    def test_strict_mode_raises_with_diagnostics(self):
        with self.assertRaises(StandardsComplianceError) as context:
            MailReader(parsing_mode=ParsingMode.STRICT).parse_bytes(b"From: a@example.com\r\n\r\nbody")
        self.assertIn("MissingRequiredDate", {item.code for item in context.exception.diagnostics})

    def test_parser_limits_are_diagnostic_and_strictly_enforceable(self):
        limits = ParserLimits(max_message_bytes=20)
        message = self.parse(limits=limits)
        self.assertIn("MessageSizeLimitExceeded", self.diagnostic_codes(message))

    def test_json_exposes_the_single_structured_schema(self):
        message = self.parse(b"Subject: hello\r\n")
        exported = json.loads(message.export_as_json())
        self.assertEqual(exported["schema_version"], 2)
        self.assertEqual(exported["subject"], "hello")
        self.assertIsInstance(exported["headers"], list)

        invalid = MailReader().parse_bytes(b"From: a@example.com\r\n\r\n")
        invalid_json = json.loads(invalid.export_as_json())
        self.assertIn("error", {item["severity"] for item in invalid_json["diagnostics"]})

    def test_attachment_name_uses_content_disposition_precedence(self):
        source = self.REQUIRED + (
            b"MIME-Version: 1.0\r\n"
            b'Content-Type: application/octet-stream; name="legacy.bin"\r\n'
            b'Content-Disposition: attachment; filename="modern.bin"\r\n\r\ndata'
        )
        attachment = MailReader().parse_bytes(source).Attachments[0]
        self.assertEqual(attachment.Name, "modern.bin")


if __name__ == "__main__":
    unittest.main()
