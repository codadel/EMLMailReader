import unittest

from EMLMailReader import ContentType


class TestContentType(unittest.TestCase):
    """
    A unit test case to check the methods exposed by 'ContentType' class.
    """

    def setUp(self) -> None:
        self.content_type = ContentType()

    def test_default_media_type(self) -> None:
        """
        Check if default media type is 'text/plain'.
        :returns: Does not return a value.
        """
        self.assertEqual(
            self.content_type.MediaType,
            "text/plain",
            "Media Type does not match the default value.",
        )

    def test_dynamic_media_type(self) -> None:
        """
        Checks if the media type returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.content_type.parse("text/html; charset=utf-8")
        self.assertEqual(
            self.content_type.MediaType,
            "text/html",
            "Media Type does not match the expected value.",
        )

    def test_content_type_charset(self) -> None:
        """
        Checks if the character set returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.content_type.parse("text/html; charset=utf-8")
        self.assertEqual(
            self.content_type.Charset,
            "utf-8",
            "Character Set does not match the expected value.",
        )
        self.content_type = ContentType()
        self.content_type.parse("multipart/form-data; boundary=absfhdjg")
        self.assertEqual(
            self.content_type.Charset,
            "us-ascii",
            "Character set does not match the default value.",
        )

    def test_content_type_boundary(self) -> None:
        """
        Checks if the boundary returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.content_type.parse("multipart/form-data; boundary=something")
        self.assertEqual(
            self.content_type.Boundary,
            "something",
            "Boundary does not match the expected value.",
        )
        self.content_type = ContentType()
        self.content_type.parse("application/pdf; charset=utf-8")
        self.assertEqual(
            self.content_type.Boundary, "", "Boundary does not match the default value."
        )

    def test_content_type_name(self) -> None:
        """
        Checks if the content type name returned by parse() matches the expected value.
        :returns: Does not return a value.
        """
        self.content_type.parse("application/octet-stream; name=52086119535.pdf")
        self.assertEqual(
            self.content_type.Name,
            "52086119535.pdf",
            "Name does not match the expected value.",
        )
        self.content_type = ContentType()
        self.content_type.parse("application/pdf; charset=utf-8")
        self.assertEqual(
            self.content_type.Name, "", "Name does not match the default value."
        )

    def test_invalid_property(self) -> None:
        """
        Checks if Invalid property error is ignored by parse(), and if it continues to process the valid properties.
        :returns: Does not return a value.
        """
        self.content_type.parse('text/plain; format="flowed"')
        self.assertEqual(
            self.content_type.MediaType,
            "text/plain",
            "Presence of invalid property should not affect the processing of valid properties.",
        )

    def test_stringify(self) -> None:
        """
        Checks if the stringified value returned, matches the expected content type value.
        :returns: Does not return a value.
        """
        self.content_type.parse(
            "application/octet-stream; name=52086119535.pdf; charset=utf-8"
        )
        self.assertEqual(
            str(self.content_type),
            'application/octet-stream; name="52086119535.pdf"; charset="utf-8"',
            "Stringified value does not match the normalized content type value.",
        )
        self.content_type = ContentType()
        self.content_type.parse("multipart/form-data; boundary=something")
        self.assertEqual(
            str(self.content_type),
            'multipart/form-data; boundary="something"',
            "Stringified value does not match the normalized content type value.",
        )


if __name__ == "__main__":
    unittest.main()
