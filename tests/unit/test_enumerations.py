import unittest

from EMLMailReader import LoggingMode, TransferEncoding, TransferEncodingValue
from EMLMailReader.Enumerations import LoggingLevel


class TestEnumerations(unittest.TestCase):
    def test_transfer_encoding_tokens_are_wire_values(self):
        self.assertEqual(TransferEncoding.BASE64.value, "base64")
        self.assertEqual(TransferEncoding.SEVEN_BIT.value, "7bit")
        self.assertEqual(TransferEncoding.EIGHT_BIT.value, "8bit")
        self.assertEqual(TransferEncoding.QUOTED_PRINTABLE.value, "quoted-printable")
        self.assertEqual(TransferEncoding.BINARY.value, "binary")
        self.assertEqual(TransferEncoding.UNKNOWN.value, "unknown")

    def test_transfer_encoding_value_preserves_extensions(self):
        known = TransferEncodingValue.parse(" BASE64 ")
        self.assertEqual(known.kind, TransferEncoding.BASE64)
        self.assertFalse(known.is_extension)

        extension = TransferEncodingValue.parse("X-Vendor")
        self.assertEqual(extension.raw_value, "x-vendor")
        self.assertEqual(extension.kind, TransferEncoding.UNKNOWN)
        self.assertTrue(extension.is_extension)
        self.assertEqual(extension.to_dict()["kind"], "unknown")

    def test_transfer_encoding_default(self):
        self.assertEqual(TransferEncodingValue.parse(None).kind, TransferEncoding.SEVEN_BIT)

    def test_logging_enums_remain_available(self):
        self.assertNotEqual(LoggingMode.CONSOLE, LoggingMode.FILE)
        self.assertNotEqual(LoggingLevel.INFO, LoggingLevel.ERROR)


if __name__ == "__main__":
    unittest.main()
