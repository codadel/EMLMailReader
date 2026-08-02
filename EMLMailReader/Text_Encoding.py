from quopri import decodestring
from base64 import b64decode
from .Custom_Exceptions import InvalidEncodingError


class TextEncoding:
    """
    Static utility class for decoding various text encodings used in MIME content.

    This class provides methods to decode Base64 and Quoted-Printable encoded content
    commonly found in email messages. It handles both text content and binary file
    attachments, with proper character set handling for internationalization.
    """
    @staticmethod
    def decode_quoted_printable_string(encoded_string: str, string_charset: str, is_header: bool) -> str:
        """
        [INTERNAL USE ONLY] Decodes Quoted-Printable encoded text content to readable string.

        Quoted-Printable encoding is used for text that contains mostly ASCII characters
        with occasional non-ASCII characters. This method handles the decoding and
        character set conversion to produce properly formatted Unicode text.

        :param encoded_string: Quoted-Printable encoded string to decode.
        :param string_charset: Character encoding of the original text (e.g., 'utf-8', 'iso-8859-1').
        :param is_header: Whether the content is from an email header (affects decoding rules).
        :returns: Decoded Unicode string with proper character encoding.
        """
        if string_charset == str():
            string_charset = "utf-8"
        decoded_value = decodestring(encoded_string, header=is_header)
        decoded_string = decoded_value.decode(string_charset)
        return decoded_string

    @staticmethod
    def decode_base64_string(encoded_string: str, string_charset: str = "utf-8") -> str:
        """
        [INTERNAL USE ONLY] Decodes Base64 encoded text content to readable string.

        Base64 encoding is commonly used for binary data and non-ASCII text in email.
        This method decodes the Base64 content and converts it to a Unicode string
        using the specified character encoding.

        :param encoded_string: Base64 encoded string to decode.
        :param string_charset: Character encoding for the decoded text (defaults to UTF-8).
        :returns: Decoded Unicode string with proper character encoding.
        """
        decoded_bytes = b64decode(encoded_string)
        decoded_string = decoded_bytes.decode(string_charset)
        return decoded_string

    @staticmethod
    def decode_base64_file(file_contents: str) -> bytes:
        """
        Decodes Base64 encoded binary file content back to original bytes.

        This method is used to extract file attachments from email messages.
        Base64 encoding allows binary files to be transmitted safely through
        text-based email systems.

        :param file_contents: Base64 encoded string representing binary file data.
        :returns: Original binary file content as bytes object.
        """
        decoded_file_contents = b64decode(file_contents)
        return decoded_file_contents

    @staticmethod
    def decode_header(encoded_string: str) -> str:
        """
        Decodes RFC 2047 encoded email headers to readable Unicode text.

        Email headers may contain encoded content in the format =?charset?encoding?data?=
        where encoding is either 'Q' (Quoted-Printable) or 'B' (Base64). This method
        detects and decodes such headers, returning plain Unicode text.

        :param encoded_string: Potentially encoded header string to decode.
        :returns: Decoded Unicode string, or original string if no encoding detected.
        :raises InvalidEncodingError: If an unsupported encoding method is encountered.
        """
        encoded_string = encoded_string.strip()
        if encoded_string.startswith("=?"):
            encoded_string = encoded_string[2:]
            encoded_string = encoded_string[0: len(encoded_string) - 2]
            string_parts = encoded_string.split("?")
            if (string_parts[1]).strip().upper() == "Q":
                decoded_string = TextEncoding.decode_quoted_printable_string(string_parts[2], string_parts[0], True)
            elif (string_parts[1]).strip().upper() == "B":
                decoded_string = TextEncoding.decode_base64_string(string_parts[2], string_parts[0])
            else:
                raise InvalidEncodingError(encoded_string)
        else:
            decoded_string = encoded_string

        return decoded_string
