import unittest
from EMLMailReader import MailAttachment, MailAttachmentCollection, ContentType, ContentDisposition


class TestMailAttachment(unittest.TestCase):
    """
    A unit test case to check the methods exposed by 'MailAttachment' class.
    """
    def setUp(self):
        self.mail_attachment = MailAttachment()
        self.content_type = ContentType()
        self.content_disposition = ContentDisposition()
        self.attachment_collection = MailAttachmentCollection()

    def test_attachment_name(self):
        """
        Checks if the file name set by parse_values() method matches the expected file name.
        :returns: Does not return a value.
        """
        # Scenario 1 :: When file name is present in Content-Type and not in Content-Disposition.
        self.content_type.parse("application/pdf; name=\"Getting started with OneDrive-CFTS-MKB.pdf\"")
        self.content_disposition.parse("attachment; size=1311269")
        self.mail_attachment.parse_values(bytes(), self.content_type, self.content_disposition, str())
        self.assertEqual(self.mail_attachment.Name, "Getting started with OneDrive-CFTS-MKB.pdf", "Attachment name does not match the Content-Type name.")

        # Scenario 2 :: When file name is present in Content-Disposition and not in Content-Type.
        self.mail_attachment = MailAttachment()
        self.content_type = ContentType()
        self.content_disposition = ContentDisposition()
        self.content_type.parse("application/pdf; charset=utf-8")
        self.content_disposition.parse("attachment; size=1311269; filename=\"Getting started with OneDrive-CFTS-MKB-1.pdf\"")
        self.mail_attachment.parse_values(bytes(), self.content_type, self.content_disposition, str())
        self.assertEqual(self.mail_attachment.Name, "Getting started with OneDrive-CFTS-MKB-1.pdf", "Attachment name does not match the Content-Disposition name.")

        # Scenario 3 :: When file name is present in both Content-Type and in Content-Disposition.
        self.mail_attachment = MailAttachment()
        self.content_type = ContentType()
        self.content_disposition = ContentDisposition()
        self.content_type.parse("application/pdf; charset=utf-8; name=\"Getting started with OneDrive-CFTS-MKB-2.pdf\"")
        self.content_disposition.parse("attachment; size=1311269; filename=\"Getting started with OneDrive-CFTS-MKB-2.pdf\"")
        self.mail_attachment.parse_values(bytes(), self.content_type, self.content_disposition, str())
        self.assertEqual(self.mail_attachment.Name, "Getting started with OneDrive-CFTS-MKB-2.pdf", "Attachment name does not match the Content-Type name.")

        # Scenario 4 :: When file name is neither present in Content-Type nor in Content-Disposition.
        self.mail_attachment = MailAttachment()
        self.content_type = ContentType()
        self.content_disposition = ContentDisposition()
        self.content_type.parse("application/pdf; charset=utf-8")
        self.content_disposition.parse("attachment; size=1311269")
        self.mail_attachment.parse_values(bytes(), self.content_type, self.content_disposition, str())
        self.assertEqual(self.mail_attachment.Name, "", "Attachment name does not match the default value.")

    def test_attachment_initialization_defaults(self):
        """
        Test MailAttachment initialization with default values.
        :returns: Does not return a value.
        """
        attachment = MailAttachment()

        self.assertEqual(attachment.Name, str(), "Name should be empty string by default.")
        self.assertIsInstance(attachment.ContentType, ContentType, "ContentType should be ContentType instance.")
        self.assertIsInstance(attachment.ContentDisposition, ContentDisposition, "ContentDisposition should be ContentDisposition instance.")
        self.assertEqual(attachment.Contents, bytes(), "Contents should be empty bytes by default.")
        self.assertEqual(attachment.ContentID, str(), "ContentID should be empty string by default.")

    def test_attachment_parse_values_content_copying(self):
        """
        Test that parse_values() creates deep copies of provided objects.
        :returns: Does not return a value.
        """
        test_contents = b"Test binary content"
        test_content_id = "content123"

        self.content_type.parse("application/pdf; name=\"test.pdf\"")
        self.content_disposition.parse("attachment; filename=\"test.pdf\"")

        # Store original values
        original_content_type_name = self.content_type.Name
        original_disposition_filename = self.content_disposition.FileName

        self.mail_attachment.parse_values(test_contents, self.content_type, self.content_disposition, test_content_id)

        # Verify deep copy by modifying originals
        self.content_type.Name = "modified.pdf"
        self.content_disposition.FileName = "modified.pdf"

        # Attachment should retain original values
        self.assertEqual(self.mail_attachment.ContentType.Name, original_content_type_name, "Should have deep copy of ContentType.")
        self.assertEqual(self.mail_attachment.ContentDisposition.FileName, original_disposition_filename, "Should have deep copy of ContentDisposition.")
        self.assertEqual(self.mail_attachment.Contents, test_contents, "Should copy contents.")
        self.assertEqual(self.mail_attachment.ContentID, test_content_id, "Should copy ContentID.")

    def test_attachment_parse_values_priority_content_type_over_disposition(self):
        """
        Test that ContentType name takes priority over ContentDisposition filename when both exist.
        :returns: Does not return a value.
        """
        self.content_type.parse("application/pdf; name=\"priority.pdf\"")
        self.content_disposition.parse("attachment; filename=\"secondary.pdf\"")

        self.mail_attachment.parse_values(b"content", self.content_type, self.content_disposition, "id")

        self.assertEqual(self.mail_attachment.Name, "priority.pdf", "ContentType name should take priority over ContentDisposition filename.")

    def test_attachment_collection_initialization(self):
        """
        Test MailAttachmentCollection initialization.
        :returns: Does not return a value.
        """
        collection = MailAttachmentCollection()

        self.assertEqual(collection.length(), 0, "Collection should be empty initially.")
        self.assertEqual(len(collection.export_as_list()), 0, "Exported list should be empty initially.")

    def test_attachment_collection_append_single(self):
        """
        Test MailAttachmentCollection append with single attachment.
        :returns: Does not return a value.
        """
        attachment = MailAttachment()
        attachment.Name = "test1.pdf"

        self.attachment_collection.append(attachment)

        self.assertEqual(self.attachment_collection.length(), 1, "Collection should have 1 attachment.")
        exported = self.attachment_collection.export_as_list()
        self.assertEqual(len(exported), 1, "Exported list should have 1 attachment.")
        self.assertEqual(exported[0].Name, "test1.pdf", "Exported attachment should have correct name.")

    def test_attachment_collection_append_multiple(self):
        """
        Test MailAttachmentCollection append with multiple attachments.
        :returns: Does not return a value.
        """
        attachment1 = MailAttachment()
        attachment1.Name = "file1.pdf"
        attachment2 = MailAttachment()
        attachment2.Name = "file2.txt"
        attachment3 = MailAttachment()
        attachment3.Name = "file3.jpg"

        self.attachment_collection.append(attachment1)
        self.attachment_collection.append(attachment2)
        self.attachment_collection.append(attachment3)

        self.assertEqual(self.attachment_collection.length(), 3, "Collection should have 3 attachments.")
        exported = self.attachment_collection.export_as_list()
        self.assertEqual(len(exported), 3, "Exported list should have 3 attachments.")

        names = [att.Name for att in exported]
        self.assertIn("file1.pdf", names, "Should contain first attachment.")
        self.assertIn("file2.txt", names, "Should contain second attachment.")
        self.assertIn("file3.jpg", names, "Should contain third attachment.")

    def test_attachment_collection_export_deep_copy(self):
        """
        Test that MailAttachmentCollection.export_as_list() returns deep copies.
        :returns: Does not return a value.
        """
        attachment = MailAttachment()
        attachment.Name = "original.pdf"
        attachment.Contents = b"original content"

        self.attachment_collection.append(attachment)
        exported = self.attachment_collection.export_as_list()

        # Modify original attachment
        attachment.Name = "modified.pdf"
        attachment.Contents = b"modified content"

        # Exported copy should remain unchanged
        self.assertEqual(exported[0].Name, "original.pdf", "Exported attachment should not be affected by original modifications.")
        self.assertEqual(exported[0].Contents, b"original content", "Exported attachment contents should not be affected.")

    def test_attachment_collection_length_consistency(self):
        """
        Test that MailAttachmentCollection.length() is consistent with export_as_list().
        :returns: Does not return a value.
        """
        # Test with various numbers of attachments
        for i in range(5):
            attachment = MailAttachment()
            attachment.Name = f"file{i}.txt"
            self.attachment_collection.append(attachment)

            # Length should match exported list length
            self.assertEqual(self.attachment_collection.length(), len(self.attachment_collection.export_as_list()),
                           f"Length should be consistent with exported list at {i+1} attachments.")

    def test_attachment_with_empty_content(self):
        """
        Test MailAttachment with empty content.
        :returns: Does not return a value.
        """
        self.content_type.parse("text/plain")
        self.content_disposition.parse("attachment")

        self.mail_attachment.parse_values(bytes(), self.content_type, self.content_disposition, str())

        self.assertEqual(self.mail_attachment.Contents, bytes(), "Should handle empty content.")
        self.assertEqual(self.mail_attachment.Name, str(), "Should have empty name when no filename provided.")

    def test_attachment_with_binary_content(self):
        """
        Test MailAttachment with various binary content types.
        :returns: Does not return a value.
        """
        binary_data = bytes(range(256))  # All possible byte values

        self.content_type.parse("application/octet-stream; name=\"binary.dat\"")
        self.content_disposition.parse("attachment")

        self.mail_attachment.parse_values(binary_data, self.content_type, self.content_disposition, "binary_id")

        self.assertEqual(self.mail_attachment.Contents, binary_data, "Should handle binary content correctly.")
        self.assertEqual(self.mail_attachment.Name, "binary.dat", "Should extract name from ContentType.")
        self.assertEqual(self.mail_attachment.ContentID, "binary_id", "Should set ContentID correctly.")

    def test_attachment_collection_empty_operations(self):
        """
        Test MailAttachmentCollection operations on empty collection.
        :returns: Does not return a value.
        """
        self.assertEqual(self.attachment_collection.length(), 0, "Empty collection should have length 0.")

        exported = self.attachment_collection.export_as_list()
        self.assertEqual(len(exported), 0, "Empty collection should export empty list.")
        self.assertIsInstance(exported, list, "Should return list type even when empty.")


if __name__ == "__main__":
    unittest.main()
