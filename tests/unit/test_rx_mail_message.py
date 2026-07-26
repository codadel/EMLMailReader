import json
import inspect
import unittest

from EMLMailReader import (
    ContentDisposition,
    ContentType,
    MailReader,
    RxMailMessage,
)


class TestRxMailMessage(unittest.TestCase):
    REQUIRED = (
        b"Date: Fri, 21 Nov 1997 09:55:06 -0600\r\n"
        b"From: alice@example.com\r\n"
    )

    def test_default_model_uses_canonical_types(self):
        message = RxMailMessage()
        self.assertEqual(message.Headers.to_list(), [])
        self.assertEqual(message.From.Mailboxes, ())
        self.assertEqual(message.ContentType.MediaType, "text/plain")
        self.assertEqual(message.Body, "")
        self.assertFalse(message.IsMultiPart)
        self.assertEqual(message.Attachments, ())
        self.assertEqual(message.InlineResources, ())

    def test_compatibility_projection_properties_are_absent(self):
        message = RxMailMessage()
        removed = (
            "HeaderFields",
            "FromAddresses",
            "SenderAddress",
            "ReplyToAddresses",
            "ToAddresses",
            "CcAddresses",
            "BccAddresses",
            "EffectiveContentType",
            "PreferredBody",
            "RawContentTransferEncoding",
            "RawMessageID",
            "ParsedMessageID",
            "RawContentID",
            "ParsedContentID",
            "RawSubject",
            "AddressLists",
            "NativeMessage",
        )
        self.assertTrue(all(not hasattr(message, name) for name in removed))
        self.assertNotIn("compatibility_mode", inspect.signature(MailReader).parameters)

    def test_body_views_are_computed_from_mime_tree(self):
        plain = RxMailMessage()
        plain.ContentType.parse("text/plain; charset=utf-8")
        plain._DecodedText = "plain"

        html = RxMailMessage()
        html.ContentType.parse("text/html; charset=utf-8")
        html._DecodedText = "<b>html</b>"

        alternative = RxMailMessage()
        alternative.ContentType.parse("multipart/alternative; boundary=x")
        alternative.Children.extend((plain, html))

        self.assertTrue(alternative.IsMultiPart)
        self.assertEqual(alternative.TextBody, "plain")
        self.assertEqual(alternative.HtmlBody, "<b>html</b>")
        self.assertEqual(alternative.Body, "<b>html</b>")

        mixed = RxMailMessage()
        mixed.ContentType.parse("multipart/mixed; boundary=y")
        mixed.Children.extend((plain, html))
        self.assertEqual(mixed.Body, "plain")

    def test_attachment_and_inline_views_reference_mime_parts(self):
        attachment = RxMailMessage()
        attachment.ContentType.parse('application/octet-stream; name="legacy.bin"')
        attachment.ContentDisposition = ContentDisposition()
        attachment.ContentDisposition.parse('attachment; filename="report.bin"')
        attachment.DecodedBody = b"payload"

        inline = RxMailMessage()
        inline.ContentType.parse("image/png")
        inline.ContentDisposition = ContentDisposition()
        inline.ContentDisposition.parse('inline; filename="pixel.png"')

        root = RxMailMessage()
        root.ContentType.parse("multipart/mixed; boundary=x")
        root.Children.extend((attachment, inline))

        self.assertIs(root.Attachments[0], attachment)
        self.assertEqual(root.Attachments[0].Name, "report.bin")
        self.assertEqual(root.InlineResources, (inline,))
        self.assertTrue(attachment.IsAttachment)
        self.assertFalse(inline.IsAttachment)
        self.assertTrue(inline.IsInline)

    def test_filename_without_disposition_is_an_attachment(self):
        part = RxMailMessage()
        part.ContentType.parse('application/octet-stream; name="data.bin"')
        self.assertTrue(part.IsAttachment)
        self.assertEqual(part.Attachments, (part,))

    def test_single_json_schema_serializes_children_once(self):
        message = MailReader().parse_bytes(self.REQUIRED + b"Subject: hello\r\n\r\nbody")
        exported = message.to_dict()
        self.assertEqual(exported["schema_version"], 2)
        self.assertEqual(exported["subject"], "hello")
        self.assertNotIn("legacy_headers", exported)
        self.assertNotIn("attachments", exported)
        self.assertEqual(json.loads(message.export_as_json()), exported)

    def test_content_type_and_disposition_helpers(self):
        content_type = ContentType()
        content_type.parse("text/plain; charset=utf-8; format=flowed")
        self.assertEqual(content_type.get_parameter("FORMAT"), "flowed")
        self.assertEqual(content_type.to_dict()["media_type"], "text/plain")

        disposition = ContentDisposition()
        disposition.parse("inline")
        self.assertEqual(disposition.to_dict()["type"], "inline")


if __name__ == "__main__":
    unittest.main()
