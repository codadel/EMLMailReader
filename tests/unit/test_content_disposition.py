import unittest

from EMLMailReader import ContentDisposition


class TestContentDisposition(unittest.TestCase):
    def test_registered_and_extension_dispositions(self):
        inline = ContentDisposition()
        inline.parse("inline; filename=photo.png")
        self.assertEqual(inline.DispositionType, "inline")
        self.assertEqual(inline.FileName, "photo.png")
        self.assertTrue(inline.IsExplicit)

        extension = ContentDisposition()
        extension.parse("render; x-mode=preview")
        self.assertEqual(extension.DispositionType, "render")
        self.assertEqual(extension.get_parameter("X-Mode"), "preview")

    def test_dates_size_and_dictionary_share_one_representation(self):
        value = (
            'attachment; filename="report.txt"; size=12; '
            'creation-date="Fri, 21 Nov 1997 09:55:06 -0600"; '
            'modification-date="broken"; '
            'read-date="Sat, 22 Nov 1997 10:00:00 -0600"'
        )
        disposition = ContentDisposition()
        disposition.parse(value)

        self.assertEqual(disposition.Size, 12)
        self.assertTrue(disposition.CreationDate.valid)
        self.assertFalse(disposition.ModificationDate.valid)
        self.assertTrue(disposition.ReadDate.valid)
        exported = disposition.to_dict()
        self.assertEqual(exported["filename"], "report.txt")
        self.assertEqual(exported["creation_date"]["valid"], True)
        self.assertEqual(exported["modification_date"]["valid"], False)

    def test_empty_and_non_numeric_parameters(self):
        disposition = ContentDisposition()
        disposition.parse("attachment; size=many")
        self.assertEqual(disposition.Size, 0)
        self.assertIsNone(disposition.CreationDate)
        self.assertIsNone(disposition.get_parameter("missing"))
        self.assertEqual(disposition.get_parameter("missing", "fallback"), "fallback")

    def test_header_serialization(self):
        disposition = ContentDisposition()
        disposition.parse('attachment; filename="hello world.txt"')
        self.assertIn("attachment", disposition.to_header_value())
        self.assertEqual(str(disposition), disposition.to_header_value())


if __name__ == "__main__":
    unittest.main()
