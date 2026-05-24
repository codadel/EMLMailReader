import unittest
import json
from EMLMailReader import ContentDisposition, DispositionType


class TestContentDisposition(unittest.TestCase):
    """
        A unit test case to check the methods exposed by 'ContentDisposition' class.
    """
    def setUp(self):
        self.content_disposition = ContentDisposition()

    def test_default_disposition_type(self):
        """
        Check if default Content Disposition Type is 'attachment'.
        :returns: Does not return a value.
        """
        self.assertEqual(self.content_disposition.DispositionType, DispositionType.ATTACHMENT, "Disposition does not match the default value.")

    def test_dynamic_filename(self):
        """
        Checks if the file name returned by parse() method matches the expected file name.
        :returns: Does not return a value.
        """
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.FileName, "Getting started with OneDrive-CFTS-MKB.pdf", "File name parsed does not match the expected value.")
        self.content_disposition = ContentDisposition()
        self.content_disposition.parse("attachment; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.FileName, "", "File name parsed is not empty.")

    def test_dynamic_disposition_type(self):
        """
        Checks if the disposition type returned by parse() matches the expected disposition type.
        :returns: Does not return a value.
        """
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.DispositionType, DispositionType.ATTACHMENT, "Disposition type does not match the expected value.")

    def test_dynamic_creation_date(self):
        """
        Checks if the creation date returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.CreationDate, "Fri, 22 Mar 2024 22:52:22 GMT", "Creation Date does not match the expected value.")
        self.content_disposition = ContentDisposition()
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.CreationDate, "", "Creation Date is not empty.")

    def test_dynamic_modification_date(self):
        """
        Checks if the modification date returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.ModificationDate, "Fri, 22 Mar 2024 22:52:22 GMT", "Modification Date does not match the expected value.")
        self.content_disposition = ContentDisposition()
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.ModificationDate, "", "Modification Date is not empty.")

    def test_dynamic_size(self):
        """
        Checks if the size returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.Size, 1311269, "Size does not match the expected value.")
        self.content_disposition = ContentDisposition()
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")
        self.assertEqual(self.content_disposition.Size, 0, "Size should be zero.")

    def test_invalid_property(self):
        """
        Checks if Invalid property error is ignored by parse(), and if it continues to process the valid properties.
        :returns: Does not return a value.
        """
        self.content_disposition.parse("attachment; fname=\"Sample File Name.pdf\"")
        self.assertEqual(self.content_disposition.DispositionType, DispositionType.ATTACHMENT, "Presence of invalid property should not affect the processing of valid properties.")

    def test_string_representation_returns_json(self):
        """
        Checks if string representation returns the parsed disposition data as JSON.
        :returns: Does not return a value.
        """
        self.content_disposition.parse("attachment; filename=\"Getting started with OneDrive-CFTS-MKB.pdf\"; size=1311269; creation-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"; modification-date=\"Fri, 22 Mar 2024 22:52:22 GMT\"")

        disposition_data = json.loads(str(self.content_disposition))

        self.assertEqual(disposition_data["Disposition-Type"], "ATTACHMENT", "Disposition type JSON value does not match.")
        self.assertEqual(disposition_data["File-Name"], "Getting started with OneDrive-CFTS-MKB.pdf", "File name JSON value does not match.")
        self.assertEqual(disposition_data["Creation-Date"], "Fri, 22 Mar 2024 22:52:22 GMT", "Creation date JSON value does not match.")
        self.assertEqual(disposition_data["Modification-Date"], "Fri, 22 Mar 2024 22:52:22 GMT", "Modification date JSON value does not match.")
        self.assertEqual(disposition_data["Size"], 1311269, "Size JSON value does not match.")


if __name__ == "__main__":
    unittest.main()
