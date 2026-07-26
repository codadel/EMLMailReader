"""Utilities for MIME transfer and encoded-header text decoding."""

from quopri import decodestring
from base64 import b64decode
from email.header import decode_header as stdlib_decode_header


class TextEncoding:
    """Decode common MIME transfer encodings and RFC 2047 header text."""

    @staticmethod
    def decode_quoted_printable_string(encoded_string: str, string_charset: str, is_header: bool) -> str:
        """Decode quoted-printable text using the supplied character set.

        Args:
            encoded_string: Quoted-printable source text.
            string_charset: Charset for decoded bytes; an empty value means
                UTF-8.
            is_header: Whether underscores use RFC 2047 header semantics.

        Returns:
            Decoded Unicode text.
        """
        if string_charset == str():
            string_charset = "utf-8"
        decoded_value = decodestring(encoded_string, header=is_header)
        decoded_string = decoded_value.decode(string_charset)
        return decoded_string

    @staticmethod
    def decode_base64_string(encoded_string: str, string_charset: str = "utf-8") -> str:
        """Decode Base64 text and convert it to Unicode.

        Args:
            encoded_string: Base64 source text.
            string_charset: Charset used to decode the resulting bytes.
        """
        decoded_bytes = b64decode(encoded_string)
        decoded_string = decoded_bytes.decode(string_charset)
        return decoded_string

    @staticmethod
    def decode_base64_file(file_contents: str) -> bytes:
        """Return the binary payload represented by Base64 source text."""
        decoded_file_contents = b64decode(file_contents)
        return decoded_file_contents

    @staticmethod
    def decode_header(encoded_string: str | None, errors: str = "replace") -> str:
        """Decode all RFC 2047 encoded words in a header value.

        Args:
            encoded_string: Encoded or plain header value. ``None`` becomes an
                empty string.
            errors: Error strategy used while converting decoded bytes.

        Returns:
            Concatenated Unicode header text.
        """
        if encoded_string is None:
            return ""
        fragments = []
        for value, charset in stdlib_decode_header(encoded_string):
            if isinstance(value, bytes):
                fragments.append(value.decode(charset or "ascii", errors))
            else:
                fragments.append(value)
        return "".join(fragments)
