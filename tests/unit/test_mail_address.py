import unittest
from unittest.mock import patch

from EMLMailReader import AddressGroup, AddressList, MailAddress


class TestMailAddress(unittest.TestCase):
    def test_mailbox_components_and_serialization(self):
        address = MailAddress()
        address.parse('"Doe, Jane" <jane@example.com>')
        self.assertEqual(address.DisplayName, "Doe, Jane")
        self.assertEqual(address.Email, "jane@example.com")
        self.assertEqual(address.LocalPart, "jane")
        self.assertEqual(address.Domain, "example.com")
        self.assertFalse(address.IsInternationalized)
        self.assertIn("jane@example.com", address.to_header_value())
        self.assertEqual(address.to_dict()["email"], "jane@example.com")

    def test_internationalized_mailbox(self):
        address = MailAddress()
        address.parse("José <josé@例え.テスト>")
        self.assertEqual(address.LocalPart, "josé")
        self.assertTrue(address.IsInternationalized)

    def test_from_parts_and_fallback_values(self):
        address = MailAddress.from_parts("Alice", "alice", "example.com")
        self.assertEqual(str(address), "Alice <alice@example.com>")

        local_only = MailAddress.from_parts("", "postmaster", "")
        self.assertEqual(local_only.Email, "postmaster")

        empty = MailAddress()
        empty.parse("")
        self.assertEqual(empty.Email, "")

    def test_address_list_preserves_groups_and_flattens_mailboxes(self):
        addresses = AddressList(
            'Team: "Doe, Jane" <jane@example.com>, bob@example.com;, carol@example.com'
        )
        self.assertIsInstance(addresses.Items[0], AddressGroup)
        self.assertEqual(addresses.Items[0].display_name, "Team")
        self.assertEqual(len(addresses.Mailboxes), 3)
        self.assertEqual(addresses.Mailboxes[0].DisplayName, "Doe, Jane")
        self.assertIn("Team:", addresses.to_header_value())
        self.assertEqual(str(addresses), addresses.to_header_value())
        self.assertEqual(len(addresses.to_dict()), 2)

    def test_empty_group_is_not_lost(self):
        addresses = AddressList("Undisclosed:;")
        self.assertEqual(len(addresses.Mailboxes), 0)
        self.assertEqual(len(addresses), 1)
        self.assertTrue(addresses)
        self.assertEqual(addresses.to_dict()[0]["type"], "group")

    def test_empty_address_list_protocols(self):
        addresses = AddressList()
        self.assertFalse(addresses)
        self.assertEqual(list(addresses), [])
        self.assertEqual(addresses.Mailboxes, ())

    def test_parser_failure_uses_lossless_fallbacks(self):
        with patch(
            "EMLMailReader.Mail_Address.HeaderParser",
            side_effect=ValueError("malformed address"),
        ):
            simple = MailAddress()
            simple.parse("not-an-address")
            self.assertEqual(simple.Email, "not-an-address")

            bracketed = MailAddress()
            bracketed.parse('"Fallback Name" <local@example.com')
            self.assertEqual(bracketed.DisplayName, "Fallback Name")
            self.assertEqual(bracketed.Email, "local@example.com")
            self.assertEqual(bracketed.LocalPart, "local")
            self.assertEqual(bracketed.Domain, "example.com")

    def test_header_rendering_failure_uses_plain_fallbacks(self):
        named = MailAddress.from_parts("Fallback Name", "local", "example.com")
        unnamed = MailAddress.from_parts("", "local", "example.com")

        with patch(
            "EMLMailReader.Mail_Address.Address",
            side_effect=ValueError("cannot render"),
        ):
            self.assertEqual(str(named), "Fallback Name <local@example.com>")
            self.assertEqual(str(unnamed), "local@example.com")


if __name__ == "__main__":
    unittest.main()
