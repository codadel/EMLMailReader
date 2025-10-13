import unittest
from EMLMailReader import MailAddress, MailAddressCollection


class TestMailAddress(unittest.TestCase):
    """
        A unit test case to check the methods exposed by 'MailAddress' class.
    """
    def setUp(self):
        self.mail_address = MailAddress()
        self.collection = MailAddressCollection()

    def test_display_name(self):
        """
        Checks if the display name returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.mail_address.parse("\"Mahesh Kumaar Balaji\" <mk.balaji@gmail.com>")
        self.assertEqual(self.mail_address.DisplayName, "Mahesh Kumaar Balaji", "Display name parsed does not match the expected value.")
        self.mail_address = MailAddress()
        self.mail_address.parse("mk.balaji@gmail.com")
        self.assertEqual(self.mail_address.DisplayName, "", "Display name parsed does not match the default value.")

    def test_email_address(self):
        """
        Checks if the email address returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.mail_address.parse("\"Mahesh Kumaar Balaji\" <mk.balaji@gmail.com>")
        self.assertEqual(self.mail_address.Email, "mk.balaji@gmail.com", "Email address parsed does not match the expected value.")
        self.mail_address = MailAddress()
        self.mail_address.parse("mk.balaji@gmail.com")
        self.assertEqual(self.mail_address.Email, "mk.balaji@gmail.com", "Email address parsed does not match the expected value.")

    def test_mail_address_stringify(self):
        """
        Checks if the stringified version od Mail Address instance matches the expected value.
        :returns: Does not return a value.
        """
        self.mail_address.parse("\"Mahesh Kumaar Balaji\" <mk.balaji@gmail.com>")
        self.assertEqual(str(self.mail_address), "Mahesh Kumaar Balaji <mk.balaji@gmail.com>", "Stringified email address returned does not match the expected value.")
        self.mail_address = MailAddress()
        self.mail_address.parse("mk.balaji@gmail.com")
        self.assertEqual(str(self.mail_address), "mk.balaji@gmail.com", "Stringified email address returned does not match the expected value.")

    def test_mail_address_collection(self):
        """
        Checks if a MailAddress instance is correctly appended to a MailAddressCollection object.
        :returns: Does not return a value.
        """
        self.mail_address.parse("\"Mahesh Kumaar Balaji\" <mk.balaji@gmail.com>")
        self.collection.append(self.mail_address)
        mail_address_one = MailAddress()
        mail_address_one.parse("mk.balaji@gmail.com")
        self.collection.append(mail_address_one)
        self.assertEqual(self.collection.length(), 2, "Length of the MailAddress collection does not match the expected value.")
        self.assertEqual(str(self.collection), "Mahesh Kumaar Balaji <mk.balaji@gmail.com>;mk.balaji@gmail.com", "Stringified email address returned does not match the expected value.")

    def test_mail_address_initialization_defaults(self):
        """
        Test MailAddress initialization with default values.
        :returns: Does not return a value.
        """
        address = MailAddress()

        self.assertEqual(address.DisplayName, "", "DisplayName should be empty by default.")
        self.assertEqual(address.Email, "", "Email should be empty by default.")

    def test_mail_address_parse_edge_cases(self):
        """
        Test MailAddress parse() method with edge cases.
        :returns: Does not return a value.
        """
        # Test with extra whitespace
        self.mail_address.parse("  \"John Doe\"   <john@example.com>  ")
        self.assertEqual(self.mail_address.DisplayName, "John Doe", "Should handle extra whitespace.")
        self.assertEqual(self.mail_address.Email, "john@example.com", "Should handle extra whitespace.")

        # Test with no display name but angle brackets
        self.mail_address = MailAddress()
        self.mail_address.parse("<simple@example.com>")
        self.assertEqual(self.mail_address.DisplayName, "", "Should have empty display name.")
        self.assertEqual(self.mail_address.Email, "simple@example.com", "Should extract email from angle brackets.")

        # Test with unquoted display name
        self.mail_address = MailAddress()
        self.mail_address.parse("John Doe <john@example.com>")
        self.assertEqual(self.mail_address.DisplayName, "John Doe", "Should handle unquoted display name.")
        self.assertEqual(self.mail_address.Email, "john@example.com", "Should extract email correctly.")

    def test_mail_address_parse_special_characters(self):
        """
        Test MailAddress parse() method with special characters in display names.
        :returns: Does not return a value.
        """
        # Test with comma in quoted display name
        self.mail_address.parse("\"Doe, John\" <john@example.com>")
        self.assertEqual(self.mail_address.DisplayName, "Doe, John", "Should handle comma in quoted display name.")
        self.assertEqual(self.mail_address.Email, "john@example.com", "Should extract email correctly.")

        # Test with special characters
        self.mail_address = MailAddress()
        self.mail_address.parse("\"John O'Connor\" <john@example.com>")
        self.assertEqual(self.mail_address.DisplayName, "John O'Connor", "Should handle apostrophe in display name.")

    def test_mail_address_parse_empty_and_invalid(self):
        """
        Test MailAddress parse() method with empty and invalid inputs.
        :returns: Does not return a value.
        """
        # Test with empty string
        self.mail_address.parse("")
        # Should handle gracefully

        # Test with just whitespace
        self.mail_address = MailAddress()
        self.mail_address.parse("   ")
        # Should handle gracefully

        # Test with malformed input
        self.mail_address = MailAddress()
        self.mail_address.parse("not an email address")
        # Should handle gracefully

    def test_mail_address_collection_initialization(self):
        """
        Test MailAddressCollection initialization.
        :returns: Does not return a value.
        """
        collection = MailAddressCollection()

        self.assertEqual(collection.length(), 0, "Collection should be empty initially.")
        self.assertEqual(str(collection), "", "Empty collection should stringify to empty string.")

    def test_mail_address_collection_append_order(self):
        """
        Test that MailAddressCollection maintains order of appended addresses.
        :returns: Does not return a value.
        """
        address1 = MailAddress()
        address1.parse("first@example.com")
        address2 = MailAddress()
        address2.parse("second@example.com")
        address3 = MailAddress()
        address3.parse("third@example.com")

        self.collection.append(address1)
        self.collection.append(address2)
        self.collection.append(address3)

        stringified = str(self.collection)
        # Check that order is maintained
        first_pos = stringified.find("first@example.com")
        second_pos = stringified.find("second@example.com")
        third_pos = stringified.find("third@example.com")

        self.assertTrue(first_pos < second_pos < third_pos, "Collection should maintain order of addresses.")

    def test_mail_address_collection_empty_operations(self):
        """
        Test MailAddressCollection operations on empty collection.
        :returns: Does not return a value.
        """
        empty_collection = MailAddressCollection()

        self.assertEqual(empty_collection.length(), 0, "Empty collection should have length 0.")
        self.assertEqual(str(empty_collection), "", "Empty collection should stringify to empty string.")

    def test_mail_address_collection_single_address(self):
        """
        Test MailAddressCollection with single address.
        :returns: Does not return a value.
        """
        address = MailAddress()
        address.parse("single@example.com")

        self.collection.append(address)

        self.assertEqual(self.collection.length(), 1, "Collection should have length 1.")
        self.assertEqual(str(self.collection), "single@example.com", "Single address should not have separator.")

    def test_mail_address_collection_multiple_with_display_names(self):
        """
        Test MailAddressCollection with multiple addresses having display names.
        :returns: Does not return a value.
        """
        address1 = MailAddress()
        address1.parse("\"First User\" <first@example.com>")
        address2 = MailAddress()
        address2.parse("\"Second User\" <second@example.com>")

        self.collection.append(address1)
        self.collection.append(address2)

        stringified = str(self.collection)
        self.assertIn("First User <first@example.com>", stringified, "Should include first address with display name.")
        self.assertIn("Second User <second@example.com>", stringified, "Should include second address with display name.")
        self.assertIn(";", stringified, "Should use semicolon separator.")

    def test_mail_address_stringify_variations(self):
        """
        Test MailAddress string representation with various formats.
        :returns: Does not return a value.
        """
        # Test with display name
        self.mail_address.parse("\"Test User\" <test@example.com>")
        self.assertEqual(str(self.mail_address), "Test User <test@example.com>", "Should format with display name and angle brackets.")

        # Test without display name
        self.mail_address = MailAddress()
        self.mail_address.parse("plain@example.com")
        self.assertEqual(str(self.mail_address), "plain@example.com", "Should format as plain email without angle brackets.")

    def test_mail_address_parse_unicode_characters(self):
        """
        Test MailAddress parse() method with Unicode characters.
        :returns: Does not return a value.
        """
        # Test with Unicode in display name
        self.mail_address.parse("\"José García\" <jose@example.com>")
        self.assertEqual(self.mail_address.DisplayName, "José García", "Should handle Unicode characters in display name.")
        self.assertEqual(self.mail_address.Email, "jose@example.com", "Should extract email correctly with Unicode display name.")

    def test_mail_address_collection_mixed_formats(self):
        """
        Test MailAddressCollection with mixed address formats.
        :returns: Does not return a value.
        """
        address1 = MailAddress()
        address1.parse("plain@example.com")
        address2 = MailAddress()
        address2.parse("\"With Name\" <withname@example.com>")
        address3 = MailAddress()
        address3.parse("<angleonly@example.com>")

        self.collection.append(address1)
        self.collection.append(address2)
        self.collection.append(address3)

        self.assertEqual(self.collection.length(), 3, "Collection should have 3 addresses.")
        stringified = str(self.collection)

        # Check all formats are represented
        self.assertIn("plain@example.com", stringified, "Plain format should be included.")
        self.assertIn("With Name <withname@example.com>", stringified, "Display name format should be included.")
        self.assertIn("angleonly@example.com", stringified, "Angle bracket only format should be included.")

    def test_mail_address_collection_duplicate_addresses(self):
        """
        Test MailAddressCollection behavior with duplicate addresses.
        :returns: Does not return a value.
        """
        address1 = MailAddress()
        address1.parse("duplicate@example.com")
        address2 = MailAddress()
        address2.parse("duplicate@example.com")

        self.collection.append(address1)
        self.collection.append(address2)

        self.assertEqual(self.collection.length(), 2, "Collection should allow duplicate addresses.")
        stringified = str(self.collection)

        # Count occurrences of the duplicate email
        count = stringified.count("duplicate@example.com")
        self.assertEqual(count, 2, "Both duplicate addresses should be present in string representation.")


if __name__ == "__main__":
    unittest.main()
