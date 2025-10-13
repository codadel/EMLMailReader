import unittest
from EMLMailReader import TransferEncoding, EntityType, DispositionType, LoggingMode
from EMLMailReader.Enumerations import LoggingLevel  # Import directly from module


class TestEnumerations(unittest.TestCase):
    """
    A unit test case to check the enumeration classes exposed by the EMLMailReader library.
    """

    def test_transfer_encoding_values(self):
        """
        Test TransferEncoding enumeration values and their integer representations.
        :returns: Does not return a value.
        """
        self.assertEqual(TransferEncoding.BASE64.value, 1, "BASE64 should have value 1.")
        self.assertEqual(TransferEncoding.SEVEN_BIT.value, 2, "SEVEN_BIT should have value 2.")
        self.assertEqual(TransferEncoding.EIGHT_BIT.value, 3, "EIGHT_BIT should have value 3.")
        self.assertEqual(TransferEncoding.QUOTED_PRINTABLE.value, 4, "QUOTED_PRINTABLE should have value 4.")

    def test_transfer_encoding_names(self):
        """
        Test TransferEncoding enumeration names.
        :returns: Does not return a value.
        """
        self.assertEqual(TransferEncoding.BASE64.name, "BASE64", "BASE64 name should be 'BASE64'.")
        self.assertEqual(TransferEncoding.SEVEN_BIT.name, "SEVEN_BIT", "SEVEN_BIT name should be 'SEVEN_BIT'.")
        self.assertEqual(TransferEncoding.EIGHT_BIT.name, "EIGHT_BIT", "EIGHT_BIT name should be 'EIGHT_BIT'.")
        self.assertEqual(TransferEncoding.QUOTED_PRINTABLE.name, "QUOTED_PRINTABLE", "QUOTED_PRINTABLE name should be 'QUOTED_PRINTABLE'.")

    def test_transfer_encoding_comparisons(self):
        """
        Test TransferEncoding enumeration comparisons and equality.
        :returns: Does not return a value.
        """
        self.assertEqual(TransferEncoding.BASE64, TransferEncoding.BASE64, "BASE64 should equal itself.")
        self.assertNotEqual(TransferEncoding.BASE64, TransferEncoding.SEVEN_BIT, "BASE64 should not equal SEVEN_BIT.")
        self.assertTrue(TransferEncoding.BASE64 != TransferEncoding.EIGHT_BIT, "BASE64 should not equal EIGHT_BIT.")

    def test_entity_type_values(self):
        """
        Test EntityType enumeration values and their integer representations.
        :returns: Does not return a value.
        """
        self.assertEqual(EntityType.ATTACHMENT.value, 1, "ATTACHMENT should have value 1.")
        self.assertEqual(EntityType.TEXT.value, 2, "TEXT should have value 2.")
        self.assertEqual(EntityType.MIME_PART.value, 3, "MIME_PART should have value 3.")

    def test_entity_type_names(self):
        """
        Test EntityType enumeration names.
        :returns: Does not return a value.
        """
        self.assertEqual(EntityType.ATTACHMENT.name, "ATTACHMENT", "ATTACHMENT name should be 'ATTACHMENT'.")
        self.assertEqual(EntityType.TEXT.name, "TEXT", "TEXT name should be 'TEXT'.")
        self.assertEqual(EntityType.MIME_PART.name, "MIME_PART", "MIME_PART name should be 'MIME_PART'.")

    def test_entity_type_comparisons(self):
        """
        Test EntityType enumeration comparisons and equality.
        :returns: Does not return a value.
        """
        self.assertEqual(EntityType.ATTACHMENT, EntityType.ATTACHMENT, "ATTACHMENT should equal itself.")
        self.assertNotEqual(EntityType.ATTACHMENT, EntityType.TEXT, "ATTACHMENT should not equal TEXT.")
        self.assertTrue(EntityType.TEXT != EntityType.MIME_PART, "TEXT should not equal MIME_PART.")

    def test_disposition_type_values(self):
        """
        Test DispositionType enumeration values and their integer representations.
        :returns: Does not return a value.
        """
        self.assertEqual(DispositionType.ATTACHMENT.value, 1, "ATTACHMENT should have value 1.")
        self.assertEqual(DispositionType.INLINE.value, 2, "INLINE should have value 2.")

    def test_disposition_type_names(self):
        """
        Test DispositionType enumeration names.
        :returns: Does not return a value.
        """
        self.assertEqual(DispositionType.ATTACHMENT.name, "ATTACHMENT", "ATTACHMENT name should be 'ATTACHMENT'.")
        self.assertEqual(DispositionType.INLINE.name, "INLINE", "INLINE name should be 'INLINE'.")

    def test_disposition_type_comparisons(self):
        """
        Test DispositionType enumeration comparisons and equality.
        :returns: Does not return a value.
        """
        self.assertEqual(DispositionType.ATTACHMENT, DispositionType.ATTACHMENT, "ATTACHMENT should equal itself.")
        self.assertNotEqual(DispositionType.ATTACHMENT, DispositionType.INLINE, "ATTACHMENT should not equal INLINE.")

    def test_logging_level_values(self):
        """
        Test LoggingLevel enumeration values and their integer representations.
        :returns: Does not return a value.
        """
        self.assertEqual(LoggingLevel.DEBUG.value, 1, "DEBUG should have value 1.")
        self.assertEqual(LoggingLevel.INFO.value, 2, "INFO should have value 2.")
        self.assertEqual(LoggingLevel.ERROR.value, 3, "ERROR should have value 3.")
        self.assertEqual(LoggingLevel.CRITICAL.value, 4, "CRITICAL should have value 4.")

    def test_logging_level_names(self):
        """
        Test LoggingLevel enumeration names.
        :returns: Does not return a value.
        """
        self.assertEqual(LoggingLevel.DEBUG.name, "DEBUG", "DEBUG name should be 'DEBUG'.")
        self.assertEqual(LoggingLevel.INFO.name, "INFO", "INFO name should be 'INFO'.")
        self.assertEqual(LoggingLevel.ERROR.name, "ERROR", "ERROR name should be 'ERROR'.")
        self.assertEqual(LoggingLevel.CRITICAL.name, "CRITICAL", "CRITICAL name should be 'CRITICAL'.")

    def test_logging_level_comparisons(self):
        """
        Test LoggingLevel enumeration comparisons and equality.
        :returns: Does not return a value.
        """
        self.assertEqual(LoggingLevel.DEBUG, LoggingLevel.DEBUG, "DEBUG should equal itself.")
        self.assertNotEqual(LoggingLevel.DEBUG, LoggingLevel.INFO, "DEBUG should not equal INFO.")
        self.assertTrue(LoggingLevel.ERROR != LoggingLevel.CRITICAL, "ERROR should not equal CRITICAL.")

    def test_logging_mode_values(self):
        """
        Test LoggingMode enumeration values and their integer representations.
        :returns: Does not return a value.
        """
        self.assertEqual(LoggingMode.CONSOLE.value, 1, "CONSOLE should have value 1.")
        self.assertEqual(LoggingMode.FILE.value, 2, "FILE should have value 2.")
        self.assertEqual(LoggingMode.NONE.value, 3, "NONE should have value 3.")

    def test_logging_mode_names(self):
        """
        Test LoggingMode enumeration names.
        :returns: Does not return a value.
        """
        self.assertEqual(LoggingMode.CONSOLE.name, "CONSOLE", "CONSOLE name should be 'CONSOLE'.")
        self.assertEqual(LoggingMode.FILE.name, "FILE", "FILE name should be 'FILE'.")
        self.assertEqual(LoggingMode.NONE.name, "NONE", "NONE name should be 'NONE'.")

    def test_logging_mode_comparisons(self):
        """
        Test LoggingMode enumeration comparisons and equality.
        :returns: Does not return a value.
        """
        self.assertEqual(LoggingMode.CONSOLE, LoggingMode.CONSOLE, "CONSOLE should equal itself.")
        self.assertNotEqual(LoggingMode.CONSOLE, LoggingMode.FILE, "CONSOLE should not equal FILE.")
        self.assertTrue(LoggingMode.FILE != LoggingMode.NONE, "FILE should not equal NONE.")

    def test_enum_uniqueness(self):
        """
        Test that all enumeration values are unique within their respective enums.
        :returns: Does not return a value.
        """
        # Test TransferEncoding uniqueness
        transfer_values = [e.value for e in TransferEncoding]
        self.assertEqual(len(transfer_values), len(set(transfer_values)), "TransferEncoding values should be unique.")

        # Test EntityType uniqueness
        entity_values = [e.value for e in EntityType]
        self.assertEqual(len(entity_values), len(set(entity_values)), "EntityType values should be unique.")

        # Test DispositionType uniqueness
        disposition_values = [e.value for e in DispositionType]
        self.assertEqual(len(disposition_values), len(set(disposition_values)), "DispositionType values should be unique.")

        # Test LoggingLevel uniqueness
        logging_level_values = [e.value for e in LoggingLevel]
        self.assertEqual(len(logging_level_values), len(set(logging_level_values)), "LoggingLevel values should be unique.")

        # Test LoggingMode uniqueness
        logging_mode_values = [e.value for e in LoggingMode]
        self.assertEqual(len(logging_mode_values), len(set(logging_mode_values)), "LoggingMode values should be unique.")

    def test_enum_iteration(self):
        """
        Test that enumerations can be properly iterated.
        :returns: Does not return a value.
        """
        # Test TransferEncoding iteration
        transfer_items = list(TransferEncoding)
        self.assertEqual(len(transfer_items), 4, "TransferEncoding should have 4 items.")
        self.assertIn(TransferEncoding.BASE64, transfer_items, "BASE64 should be in TransferEncoding.")

        # Test EntityType iteration
        entity_items = list(EntityType)
        self.assertEqual(len(entity_items), 3, "EntityType should have 3 items.")
        self.assertIn(EntityType.TEXT, entity_items, "TEXT should be in EntityType.")

        # Test DispositionType iteration
        disposition_items = list(DispositionType)
        self.assertEqual(len(disposition_items), 2, "DispositionType should have 2 items.")
        self.assertIn(DispositionType.INLINE, disposition_items, "INLINE should be in DispositionType.")

        # Test LoggingLevel iteration
        logging_level_items = list(LoggingLevel)
        self.assertEqual(len(logging_level_items), 4, "LoggingLevel should have 4 items.")
        self.assertIn(LoggingLevel.ERROR, logging_level_items, "ERROR should be in LoggingLevel.")

        # Test LoggingMode iteration
        logging_mode_items = list(LoggingMode)
        self.assertEqual(len(logging_mode_items), 3, "LoggingMode should have 3 items.")
        self.assertIn(LoggingMode.NONE, logging_mode_items, "NONE should be in LoggingMode.")


if __name__ == "__main__":
    unittest.main()
