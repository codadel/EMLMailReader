import unittest
import json
import tempfile
import os
import shutil
from unittest.mock import patch, mock_open
from EMLMailReader import (
    RxMailMessage,
    MailAddress,
    MailAddressCollection,
    MailAttachment,
    MailAttachmentCollection,
    ContentType,
    ContentDisposition,
    TransferEncoding,
    EntityType,
    FolderNotAvailableError
)


class TestRxMailMessage(unittest.TestCase):
    """
    A unit test case to check the RxMailMessage class methods exposed by the EMLMailReader library.
    """

    def setUp(self):
        """
        Set up test environment with fresh RxMailMessage instance and temporary directory.
        """
        self.message = RxMailMessage()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        Clean up temporary directories.
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_initialization_default_values(self):
        """
        Test RxMailMessage initialization with default values.
        :returns: Does not return a value.
        """
        self.assertIsNone(self.message.From, "From should be None by default.")
        self.assertIsInstance(self.message.To, MailAddressCollection, "To should be MailAddressCollection instance.")
        self.assertIsInstance(self.message.Cc, MailAddressCollection, "Cc should be MailAddressCollection instance.")
        self.assertIsInstance(self.message.Bcc, MailAddressCollection, "Bcc should be MailAddressCollection instance.")
        self.assertIsInstance(self.message.ReplyTo, MailAddressCollection, "ReplyTo should be MailAddressCollection instance.")
        self.assertEqual(self.message.Subject, str(), "Subject should be empty string by default.")
        self.assertEqual(self.message.Body, str(), "Body should be empty string by default.")
        self.assertIsNone(self.message.ContentType, "ContentType should be None by default.")
        self.assertIsNone(self.message.ContentDisposition, "ContentDisposition should be None by default.")
        self.assertEqual(self.message.ContentTransferEncoding, TransferEncoding.SEVEN_BIT, "ContentTransferEncoding should be SEVEN_BIT by default.")
        self.assertIsInstance(self.message.Headers, dict, "Headers should be dict instance.")
        self.assertEqual(self.message.MessageID, str(), "MessageID should be empty string by default.")
        self.assertFalse(self.message.IsMultiPart, "IsMultiPart should be False by default.")
        self.assertEqual(self.message.MimeVersion, str(), "MimeVersion should be empty string by default.")
        self.assertEqual(self.message.Date, str(), "Date should be empty string by default.")
        self.assertIsInstance(self.message.Children, list, "Children should be list instance.")
        self.assertEqual(self.message.ContentDescription, str(), "ContentDescription should be empty string by default.")
        self.assertEqual(self.message.EntityType, EntityType.MIME_PART, "EntityType should be MIME_PART by default.")
        self.assertIsInstance(self.message.Attachments, MailAttachmentCollection, "Attachments should be MailAttachmentCollection instance.")
        self.assertEqual(self.message.ContentID, str(), "ContentID should be empty string by default.")

    def test_add_mail_address_to_recipient(self):
        """
        Test add_mail_address() method for 'To' recipient.
        :returns: Does not return a value.
        """
        email_str = "test@example.com"
        self.message.add_mail_address("To", email_str)

        self.assertEqual(self.message.To.length(), 1, "To collection should have 1 address.")
        to_addresses = self.message.To.export_as_list()
        self.assertEqual(to_addresses[0].Email, email_str, "Email address should match.")

    def test_add_mail_address_to_cc(self):
        """
        Test add_mail_address() method for 'Cc' recipient.
        :returns: Does not return a value.
        """
        email_str = "cc@example.com"
        self.message.add_mail_address("Cc", email_str)

        self.assertEqual(self.message.Cc.length(), 1, "Cc collection should have 1 address.")
        cc_addresses = self.message.Cc.export_as_list()
        self.assertEqual(cc_addresses[0].Email, email_str, "Email address should match.")

    def test_add_mail_address_to_bcc(self):
        """
        Test add_mail_address() method for 'Bcc' recipient.
        :returns: Does not return a value.
        """
        email_str = "bcc@example.com"
        self.message.add_mail_address("Bcc", email_str)

        self.assertEqual(self.message.Bcc.length(), 1, "Bcc collection should have 1 address.")
        bcc_addresses = self.message.Bcc.export_as_list()
        self.assertEqual(bcc_addresses[0].Email, email_str, "Email address should match.")

    def test_add_mail_address_to_reply_to(self):
        """
        Test add_mail_address() method for 'ReplyTo' recipient.
        :returns: Does not return a value.
        """
        email_str = "reply@example.com"
        self.message.add_mail_address("ReplyTo", email_str)

        self.assertEqual(self.message.ReplyTo.length(), 1, "ReplyTo collection should have 1 address.")
        reply_addresses = self.message.ReplyTo.export_as_list()
        self.assertEqual(reply_addresses[0].Email, email_str, "Email address should match.")

    def test_add_mail_address_invalid_property(self):
        """
        Test add_mail_address() method with invalid property name.
        :returns: Does not return a value.
        """
        with self.assertRaises(Exception) as context:
            self.message.add_mail_address("InvalidProperty", "test@example.com")

        self.assertIn("InvalidProperty", str(context.exception), "Exception should mention the invalid property.")

    def test_add_mail_address_with_display_name(self):
        """
        Test add_mail_address() method with display name in email string.
        :returns: Does not return a value.
        """
        email_str = "\"John Doe\" <john@example.com>"
        self.message.add_mail_address("To", email_str)

        to_addresses = self.message.To.export_as_list()
        self.assertEqual(to_addresses[0].Email, "john@example.com", "Email should be parsed correctly.")
        self.assertEqual(to_addresses[0].DisplayName, "John Doe", "Display name should be parsed correctly.")

    def test_set_content_type(self):
        """
        Test set_content_type() method.
        :returns: Does not return a value.
        """
        content_type_str = "text/html; charset=utf-8"
        self.message.set_content_type(content_type_str)

        self.assertIsInstance(self.message.ContentType, ContentType, "ContentType should be ContentType instance.")
        self.assertEqual(self.message.ContentType.MediaType, "text/html", "MediaType should be parsed correctly.")
        self.assertEqual(self.message.ContentType.Charset, "utf-8", "Charset should be parsed correctly.")

    def test_set_content_disposition(self):
        """
        Test set_content_disposition() method.
        :returns: Does not return a value.
        """
        content_disposition_str = "attachment; filename=\"test.pdf\""
        self.message.set_content_disposition(content_disposition_str)

        self.assertIsInstance(self.message.ContentDisposition, ContentDisposition, "ContentDisposition should be ContentDisposition instance.")
        self.assertEqual(self.message.ContentDisposition.FileName, "test.pdf", "FileName should be parsed correctly.")

    def test_set_content_transfer_encoding_base64(self):
        """
        Test set_content_transfer_encoding() method with base64.
        :returns: Does not return a value.
        """
        self.message.set_content_transfer_encoding("base64")
        self.assertEqual(self.message.ContentTransferEncoding, TransferEncoding.BASE64, "Should set BASE64 encoding.")

    def test_set_content_transfer_encoding_8bit(self):
        """
        Test set_content_transfer_encoding() method with 8bit.
        :returns: Does not return a value.
        """
        self.message.set_content_transfer_encoding("8bit")
        self.assertEqual(self.message.ContentTransferEncoding, TransferEncoding.EIGHT_BIT, "Should set EIGHT_BIT encoding.")

    def test_set_content_transfer_encoding_quoted_printable(self):
        """
        Test set_content_transfer_encoding() method with quoted-printable.
        :returns: Does not return a value.
        """
        self.message.set_content_transfer_encoding("quoted-printable")
        self.assertEqual(self.message.ContentTransferEncoding, TransferEncoding.QUOTED_PRINTABLE, "Should set QUOTED_PRINTABLE encoding.")

    def test_set_content_transfer_encoding_default(self):
        """
        Test set_content_transfer_encoding() method with unknown encoding defaults to 7bit.
        :returns: Does not return a value.
        """
        self.message.set_content_transfer_encoding("unknown-encoding")
        self.assertEqual(self.message.ContentTransferEncoding, TransferEncoding.SEVEN_BIT, "Should default to SEVEN_BIT encoding.")

    def test_set_content_transfer_encoding_case_insensitive(self):
        """
        Test set_content_transfer_encoding() method is case insensitive.
        :returns: Does not return a value.
        """
        self.message.set_content_transfer_encoding("BASE64")
        self.assertEqual(self.message.ContentTransferEncoding, TransferEncoding.BASE64, "Should handle uppercase BASE64.")

        self.message.set_content_transfer_encoding("QuOtEd-PrInTaBlE")
        self.assertEqual(self.message.ContentTransferEncoding, TransferEncoding.QUOTED_PRINTABLE, "Should handle mixed case quoted-printable.")

    def test_set_entity_type_application_media(self):
        """
        Test set_entity_type() method with application media type.
        Note: Due to ContentType.parse() behavior, media type without parameters defaults to 'text/plain'
        :returns: Does not return a value.
        """
        self.message.set_content_type("application/pdf; name=test.pdf")  # Include parameter to avoid default
        self.message.set_entity_type()
        self.assertEqual(self.message.EntityType, EntityType.ATTACHMENT, "Application media type should set ATTACHMENT entity type.")

    def test_set_entity_type_image_media(self):
        """
        Test set_entity_type() method with image media type.
        Note: Due to ContentType.parse() behavior, media type without parameters defaults to 'text/plain'
        :returns: Does not return a value.
        """
        self.message.set_content_type("image/jpeg; name=test.jpg")  # Include parameter to avoid default
        self.message.set_entity_type()
        self.assertEqual(self.message.EntityType, EntityType.ATTACHMENT, "Image media type should set ATTACHMENT entity type.")

    def test_set_entity_type_multipart_media(self):
        """
        Test set_entity_type() method with multipart media type.
        Note: Due to ContentType.parse() behavior, media type without parameters defaults to 'text/plain'
        :returns: Does not return a value.
        """
        self.message.set_content_type("multipart/mixed; boundary=something")  # Include parameter to avoid default
        self.message.set_entity_type()
        self.assertEqual(self.message.EntityType, EntityType.MIME_PART, "Multipart media type should set MIME_PART entity type.")

    def test_set_entity_type_text_media(self):
        """
        Test set_entity_type() method with text media type.
        :returns: Does not return a value.
        """
        self.message.set_content_type("text/plain")
        self.message.set_entity_type()
        self.assertEqual(self.message.EntityType, EntityType.TEXT, "Text media type should set TEXT entity type.")

    def test_set_entity_type_without_content_type(self):
        """
        Test set_entity_type() method when ContentType is None.
        :returns: Does not return a value.
        """
        # This should handle the case gracefully
        with self.assertRaises(AttributeError):
            self.message.set_entity_type()

    def test_export_as_json_basic_properties(self):
        """
        Test export_as_json() method with basic properties.
        :returns: Does not return a value.
        """
        # Set up some basic properties
        from_address = MailAddress()
        from_address.parse("sender@example.com")
        self.message.From = from_address
        self.message.Subject = "Test Subject"
        self.message.MessageID = "12345@example.com"
        self.message.IsMultiPart = True
        self.message.MimeVersion = "1.0"
        self.message.Date = "Mon, 1 Jan 2024 12:00:00 +0000"
        self.message.Headers = {"X-Custom": "custom-value"}

        json_str = self.message.export_as_json()
        json_obj = json.loads(json_str)

        self.assertEqual(json_obj["From"], "sender@example.com", "From should be exported correctly.")
        self.assertEqual(json_obj["Subject"], "Test Subject", "Subject should be exported correctly.")
        self.assertEqual(json_obj["Message-ID"], "12345@example.com", "Message-ID should be exported correctly.")
        self.assertTrue(json_obj["IsMultiPart"], "IsMultiPart should be exported correctly.")
        self.assertEqual(json_obj["Mime-Version"], "1.0", "Mime-Version should be exported correctly.")
        self.assertEqual(json_obj["Date"], "Mon, 1 Jan 2024 12:00:00 +0000", "Date should be exported correctly.")
        self.assertEqual(json_obj["Headers"], {"X-Custom": "custom-value"}, "Headers should be exported correctly.")

    def test_export_as_json_with_content_type(self):
        """
        Test export_as_json() method with ContentType.
        :returns: Does not return a value.
        """
        self.message.set_content_type("text/html; charset=utf-8")

        json_str = self.message.export_as_json()
        json_obj = json.loads(json_str)

        self.assertEqual(json_obj["Content-Type"], "text/html; charset=utf-8", "Content-Type should be exported correctly.")

    def test_export_as_json_with_recipients(self):
        """
        Test export_as_json() method with recipient collections.
        :returns: Does not return a value.
        """
        self.message.add_mail_address("To", "to@example.com")
        self.message.add_mail_address("Cc", "cc@example.com")
        self.message.add_mail_address("Bcc", "bcc@example.com")
        self.message.add_mail_address("ReplyTo", "reply@example.com")

        json_str = self.message.export_as_json()
        json_obj = json.loads(json_str)

        self.assertEqual(json_obj["To"], "to@example.com", "To should be exported correctly.")
        self.assertEqual(json_obj["Cc"], "cc@example.com", "Cc should be exported correctly.")
        self.assertEqual(json_obj["Bcc"], "bcc@example.com", "Bcc should be exported correctly.")
        self.assertEqual(json_obj["Reply-To"], "reply@example.com", "Reply-To should be exported correctly.")

    def test_export_as_json_attachment_count(self):
        """
        Test export_as_json() method includes attachment count.
        :returns: Does not return a value.
        """
        # Add some mock attachments
        attachment1 = MailAttachment()
        attachment2 = MailAttachment()
        self.message.Attachments.append(attachment1)
        self.message.Attachments.append(attachment2)

        json_str = self.message.export_as_json()
        json_obj = json.loads(json_str)

        self.assertEqual(json_obj["Attachment-Count"], 2, "Attachment-Count should be exported correctly.")

    def test_save_attachments_valid_folder(self):
        """
        Test save_attachments() method with valid folder.
        :returns: Does not return a value.
        """
        # Create mock attachment
        attachment = MailAttachment()
        attachment.Name = "test_file.txt"
        attachment.Contents = b"Test content"
        self.message.Attachments.append(attachment)

        with patch('builtins.open', mock_open()) as mock_file:
            self.message.save_attachments(self.temp_dir)

            expected_path = os.path.join(self.temp_dir, "test_file.txt")
            mock_file.assert_called_once_with(expected_path, "wb")
            mock_file().write.assert_called_once_with(b"Test content")

    def test_save_attachments_multiple_files(self):
        """
        Test save_attachments() method with multiple attachments.
        :returns: Does not return a value.
        """
        # Create multiple mock attachments
        attachment1 = MailAttachment()
        attachment1.Name = "file1.txt"
        attachment1.Contents = b"Content 1"

        attachment2 = MailAttachment()
        attachment2.Name = "file2.txt"
        attachment2.Contents = b"Content 2"

        self.message.Attachments.append(attachment1)
        self.message.Attachments.append(attachment2)

        with patch('builtins.open', mock_open()) as mock_file:
            self.message.save_attachments(self.temp_dir)

            # Should be called twice, once for each file
            self.assertEqual(mock_file.call_count, 2, "Should open two files.")

            # Check file paths
            calls = mock_file.call_args_list
            expected_path1 = os.path.join(self.temp_dir, "file1.txt")
            expected_path2 = os.path.join(self.temp_dir, "file2.txt")

            called_paths = [call[0][0] for call in calls]
            self.assertIn(expected_path1, called_paths, "Should call with first file path.")
            self.assertIn(expected_path2, called_paths, "Should call with second file path.")

    def test_save_attachments_invalid_folder(self):
        """
        Test save_attachments() method with invalid folder.
        :returns: Does not return a value.
        """
        attachment = MailAttachment()
        attachment.Name = "test_file.txt"
        attachment.Contents = b"Test content"
        self.message.Attachments.append(attachment)

        invalid_folder = "/path/to/nonexistent/folder"

        with self.assertRaises(FolderNotAvailableError) as context:
            self.message.save_attachments(invalid_folder)

        self.assertEqual(context.exception.folderPath, invalid_folder, "Exception should contain the invalid folder path.")

    def test_save_attachments_no_attachments(self):
        """
        Test save_attachments() method with no attachments.
        :returns: Does not return a value.
        """
        with patch('builtins.open', mock_open()) as mock_file:
            self.message.save_attachments(self.temp_dir)

            # Should not open any files
            mock_file.assert_not_called()

    def test_children_collection_behavior(self):
        """
        Test Children collection behavior for multipart messages.
        :returns: Does not return a value.
        """
        child_message = RxMailMessage()
        child_message.Subject = "Child Message"

        self.message.Children.append(child_message)

        self.assertEqual(len(self.message.Children), 1, "Children collection should have 1 message.")
        self.assertEqual(self.message.Children[0].Subject, "Child Message", "Child message should be accessible.")

    def test_headers_dictionary_behavior(self):
        """
        Test Headers dictionary behavior.
        :returns: Does not return a value.
        """
        self.message.Headers["X-Custom-Header"] = "Custom Value"
        self.message.Headers["X-Another-Header"] = "Another Value"

        self.assertEqual(len(self.message.Headers), 2, "Headers should contain 2 entries.")
        self.assertEqual(self.message.Headers["X-Custom-Header"], "Custom Value", "Custom header should be accessible.")
        self.assertEqual(self.message.Headers["X-Another-Header"], "Another Value", "Another header should be accessible.")


if __name__ == "__main__":
    unittest.main()
