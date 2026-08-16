import base64
import unittest

from EMLMailReader import TextEncoding


class TestTextEncoding(unittest.TestCase):
    def test_header_decoder_handles_adjacent_and_mixed_words(self) -> None:
        value = "=?utf-8?Q?Hello_=E2=9C=93?= plain =?iso-8859-1?Q?caf=E9?="
        self.assertEqual(TextEncoding.decode_header(value), "Hello ✓ plain café")
        self.assertEqual(TextEncoding.decode_header("plain"), "plain")
        self.assertEqual(TextEncoding.decode_header(None), "")

    def test_header_decoder_replaces_invalid_bytes(self) -> None:
        value = "=?ascii?b?/w==?="
        self.assertEqual(TextEncoding.decode_header(value), "�")

    def test_base64_text_and_file_decoders(self) -> None:
        encoded = base64.b64encode("hello ✓".encode()).decode()
        self.assertEqual(TextEncoding.decode_base64_string(encoded), "hello ✓")
        self.assertEqual(TextEncoding.decode_base64_file(encoded), "hello ✓".encode())

    def test_quoted_printable_decoder(self) -> None:
        self.assertEqual(
            TextEncoding.decode_quoted_printable_string("caf=C3=A9", "utf-8", False),
            "café",
        )
        self.assertEqual(
            TextEncoding.decode_quoted_printable_string("plain", "", False),
            "plain",
        )


if __name__ == "__main__":
    unittest.main()
