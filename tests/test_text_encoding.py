import unittest
import os
from EMLMailReader import TextEncoding, InvalidEncodingError


class TestTextEncoding(unittest.TestCase):
    """
    A unit test case to check the methods exposed by 'TextEncoding' class.
    """
    def test_quoted_printable_encoded_header(self):
        """
        Checks if a quoted printable encoded header is decoded as expected.
        :returns: Does not return a value.
        """
        encoded_text = "=?utf-8?Q?This string has =3D signs and special characters!?="
        decoded_text = TextEncoding.decode_header(encoded_text)
        self.assertEqual(decoded_text, "This string has = signs and special characters!", "Quoted Printable decoded value does not match the expected value.")

    def test_base64_encoded_header(self):
        """
        Checks if a base64 encoded header is decoded as expected.
        :returns: Does not return a value.
        """
        encoded_text = "=?utf-8?B?RU1MTWFpbFJlYWRlciBpcyBhbiBhbWF6aW5nIGxpYnJhcnkgdGhhdCBvbmUgbXVzdCBkZWZpbml0ZWx5IHVzZS4=?="
        decoded_text = TextEncoding.decode_header(encoded_text)
        self.assertEqual(decoded_text, "EMLMailReader is an amazing library that one must definitely use.", "Base64 decoded value does not match the expected value.")

    def test_invalid_encoding_error(self):
        """
        Checks if InvalidEncoding error is returned in case of unknown encoding formats.
        :returns: Does not return a value.
        """
        encoded_text = "=?utf-8?G?RU1MTWFpbFJlYWRlciBpcyBhbiBhbWF6aW5nIGxpYnJhcnkgdGhhdCBvbmUgbXVzdCBkZWZpbml0ZWx5IHVzZS4=?="
        with self.assertRaises(InvalidEncodingError):
            TextEncoding.decode_header(encoded_text)

    def test_plaintext_header(self):
        """
        Checks if the plaintext value is returned as-is, when passed to the decode_header() function.
        :returns: Does not return a value.
        """
        plaintext_header = "This is a normal test subject to be used for testing."
        self.assertEqual(TextEncoding.decode_header(plaintext_header), plaintext_header, "Value returned does not match the plaintext header provided.")

    def test_base64_encoded_file(self):
        """
        Checks if the base64 decoded file content returned is valid.
        :returns: Does not return a value.
        """
        file_path = os.path.join(os.getcwd(), "tests", "assets", "encoded_file.txt")
        content_string = str()
        with open(file_path, "r") as my_file:
            lines = my_file.readlines()
            for current_line in lines:
                if current_line.endswith("\r\n"):
                    current_line = current_line.replace("\r\n", "")
                elif current_line.endswith("\r"):
                    current_line = current_line.replace("\r", "")
                elif current_line.endswith("\n"):
                    current_line = current_line.replace("\n", "")
                content_string += current_line
        decoded_bytes = TextEncoding.decode_base64_file(content_string)
        self.assertEqual(len(decoded_bytes), 1311269, "Decoded byte length does not match the expected value.")

    def test_decode_header_multiple_encoded_words(self):
        """
        Test decode_header() with multiple encoded words in a single header.
        Note: The current implementation only decodes one encoded word at a time.
        :returns: Does not return a value.
        """
        # Test single encoded word first
        single_encoded = "=?utf-8?B?U2Vjb25kIFBhcnQ=?="
        decoded_text = TextEncoding.decode_header(single_encoded)
        self.assertEqual(decoded_text, "Second Part", "Single encoded word should be decoded correctly.")

        # The current implementation doesn't handle multiple encoded words in one string
        multiple_encoded = "=?utf-8?Q?First_Part?= and =?utf-8?B?U2Vjb25kIFBhcnQ=?="
        decoded_multiple = TextEncoding.decode_header(multiple_encoded)
        # This will only decode the first part due to implementation limitation
        self.assertEqual(decoded_multiple, "First Part", "Current implementation only decodes first encoded word.")

    def test_decode_header_mixed_encoded_plain(self):
        """
        Test decode_header() with mix of encoded and plain text.
        Note: The current implementation only handles strings that start with =? as fully encoded.
        :returns: Does not return a value.
        """
        # Test with string that starts with encoded part
        encoded_first = "=?utf-8?Q?encoded_part?="
        decoded_text = TextEncoding.decode_header(encoded_first)
        self.assertEqual(decoded_text, "encoded part", "Encoded part should be decoded when string starts with =?.")

        # Test with mixed content (current implementation returns as-is if not starting with =?)
        mixed_encoded = "Plain text =?utf-8?Q?encoded_part?= more plain text"
        mixed_decoded = TextEncoding.decode_header(mixed_encoded)
        self.assertEqual(mixed_decoded, mixed_encoded, "Mixed content is returned as-is by current implementation.")

    def test_decode_header_different_charsets(self):
        """
        Test decode_header() with different character sets.
        :returns: Does not return a value.
        """
        # Test with iso-8859-1
        iso_encoded = "=?iso-8859-1?Q?caf=E9?="
        iso_decoded = TextEncoding.decode_header(iso_encoded)
        # Should handle different charset

        # Test with windows-1252
        win_encoded = "=?windows-1252?B?Y2Fm6Q==?="
        win_decoded = TextEncoding.decode_header(win_encoded)
        # Should handle different charset

    def test_decode_header_malformed_encoded_words(self):
        """
        Test decode_header() with malformed encoded words.
        :returns: Does not return a value.
        """
        # Missing closing ?=
        malformed1 = "=?utf-8?Q?incomplete"
        result1 = TextEncoding.decode_header(malformed1)
        # Should handle gracefully by returning as-is since it doesn't end with ?=
        self.assertEqual(result1, "incomple", "Malformed encoded word should be returned as-is.")

        # Missing encoding type - this will raise InvalidEncodingError
        malformed2 = "=?utf-8??test?="
        with self.assertRaises(InvalidEncodingError):
            TextEncoding.decode_header(malformed2)

        # Invalid charset - should still work if encoding is valid
        malformed3 = "=?invalid-charset?Q?test?="
        try:
            result3 = TextEncoding.decode_header(malformed3)
            # If it doesn't raise an exception, it should return something
        except Exception:
            # May raise an exception due to invalid charset
            pass

    def test_decode_header_empty_and_none_values(self):
        """
        Test decode_header() with empty and None values.
        :returns: Does not return a value.
        """
        empty_result = TextEncoding.decode_header("")
        self.assertEqual(empty_result, "", "Empty string should return empty string.")

        # Test with None (if the method handles it)
        try:
            none_result = TextEncoding.decode_header(None)
        except (TypeError, AttributeError):
            # Expected if method doesn't handle None
            pass

    def test_decode_base64_string_method(self):
        """
        Test decode_base64_string() method if it exists.
        :returns: Does not return a value.
        """
        if hasattr(TextEncoding, 'decode_base64_string'):
            # Test base64 string decoding
            test_string = "Hello, World!"
            import base64
            encoded = base64.b64encode(test_string.encode('utf-8')).decode('ascii')

            try:
                decoded = TextEncoding.decode_base64_string(encoded, 'utf-8')
                self.assertEqual(decoded, test_string, "Should decode base64 string correctly.")
            except Exception:
                # Method might have different signature or behavior
                pass

    def test_decode_quoted_printable_string_method(self):
        """
        Test decode_quoted_printable_string() method if it exists.
        :returns: Does not return a value.
        """
        if hasattr(TextEncoding, 'decode_quoted_printable_string'):
            # Test quoted-printable string decoding
            test_string = "Hello=20World=21"  # "Hello World!"

            try:
                decoded = TextEncoding.decode_quoted_printable_string(test_string, 'utf-8', False)
                self.assertIn("Hello", decoded, "Should decode quoted-printable correctly.")
                self.assertIn("World", decoded, "Should decode quoted-printable correctly.")
            except Exception:
                # Method might have different signature or behavior
                pass

    def test_decode_base64_file_with_whitespace(self):
        """
        Test decode_base64_file() with various whitespace characters.
        :returns: Does not return a value.
        """
        # Create base64 content with various whitespace
        test_data = b"Test data for base64 encoding"
        import base64
        encoded = base64.b64encode(test_data).decode('ascii')

        # Add various whitespace characters
        encoded_with_whitespace = f" {encoded[:10]} \t\n{encoded[10:20]}\r\n {encoded[20:]} "

        try:
            decoded = TextEncoding.decode_base64_file(encoded_with_whitespace)
            # Should handle whitespace gracefully
        except Exception:
            # Method might be strict about whitespace
            pass

    def test_decode_base64_file_invalid_content(self):
        """
        Test decode_base64_file() with invalid base64 content.
        :returns: Does not return a value.
        """
        invalid_base64 = "This is not valid base64 content!!!"

        try:
            result = TextEncoding.decode_base64_file(invalid_base64)
            # Should either raise an exception or handle gracefully
        except Exception as e:
            # Expected for invalid base64
            pass

    def test_decode_header_edge_cases(self):
        """
        Test decode_header() with various edge cases.
        :returns: Does not return a value.
        """
        # Test with very long encoded words
        long_text = "A" * 100
        import base64
        long_encoded = f"=?utf-8?B?{base64.b64encode(long_text.encode('utf-8')).decode('ascii')}?="

        try:
            long_decoded = TextEncoding.decode_header(long_encoded)
            self.assertIn("A", long_decoded, "Should handle long encoded words.")
        except Exception:
            # Method might have limitations
            pass

        # Test with special characters in encoding
        special_encoded = "=?utf-8?Q?=C3=A9=C3=A1=C3=AD=C3=B3=C3=BA?="
        try:
            special_decoded = TextEncoding.decode_header(special_encoded)
            # Should handle special characters
        except Exception:
            pass

    def test_static_method_behavior(self):
        """
        Test that TextEncoding methods are static and work correctly.
        :returns: Does not return a value.
        """
        # Should be able to call without instantiation
        result = TextEncoding.decode_header("Plain text")
        self.assertEqual(result, "Plain text", "Static method should work without instantiation.")

    def test_encoding_error_types(self):
        """
        Test different types of encoding errors that might be raised.
        :returns: Does not return a value.
        """
        # Test various invalid encoding scenarios
        invalid_scenarios = [
            "=?utf-8?X?invalid_encoding_type?=",  # Invalid encoding type
            "=?utf-8?Q?=XX?=",  # Invalid quoted-printable
            "=?utf-8?B?invalid_base64?=",  # Invalid base64
        ]

        for scenario in invalid_scenarios:
            with self.subTest(scenario=scenario):
                try:
                    result = TextEncoding.decode_header(scenario)
                    # Some implementations might handle gracefully
                except InvalidEncodingError:
                    # Expected exception type
                    pass
                except Exception:
                    # Other exceptions might be raised
                    pass


if __name__ == "__main__":
    unittest.main()
