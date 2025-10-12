class ContentType:
    """
    A class to represent the Content-Type header of a MIME entity.

    This class parses and stores information from the Content-Type header,
    including media type, character set, boundary values for multipart content,
    and name parameters as defined in RFC 2045.
    """
    def __init__(self):
        self.MediaType = "text/plain"
        """The main media type and subtype (e.g., 'text/plain', 'image/jpeg')."""
        self.Charset = "us-ascii"
        """Character encoding used for text content (defaults to US-ASCII per RFC 2045)."""
        self.Boundary = str()
        """Delimiter string used to separate parts in multipart MIME entities."""
        self.Name = str()
        """Suggested name for the content, often used for attachments."""

    def parse(self, ContentTypeString: str = "text/plain; charset=us-ascii"):
        """
        Parses a Content-Type header string and populates the object's properties.

        This method extracts the media type and associated parameters (charset, boundary, name)
        from the header string. If no Content-Type is provided or it's invalid, defaults to
        'text/plain;charset=us-ascii' as specified in RFC 2045.

        :param ContentTypeString: The Content-Type header value to parse.
        :returns: None - modifies the object's properties in place.
        """
        ContentTypeString = ContentTypeString.strip()
        if ContentTypeString.find(";") != -1:
            ContentTypeValues = ContentTypeString.split(";")
            self.MediaType = ContentTypeValues[0]
            for index in range(1, len(ContentTypeValues)):
                Current_Value = ContentTypeValues[index]
                index_one = Current_Value.find("\"")
                if index_one == -1:
                    key = Current_Value.split("=")[0]
                    value = Current_Value.split("=")[1]
                else:
                    key = Current_Value[0:index_one]
                    key = key.strip("=")
                    Current_Value = Current_Value.replace(key + "=\"", "")
                    index_two = Current_Value.find("\"")
                    value = Current_Value[0:index_two]

                if key.lower().strip() == "charset":
                    self.Charset = value.strip().lower()
                elif key.lower().strip() == "boundary":
                    self.Boundary = value.strip()
                elif key.lower().strip() == "name":
                    self.Name = value.strip()
                else:
                    continue
        else:
            self.MediaType = "text/plain"
            self.Charset = "us-ascii"

    def __str__(self) -> str:
        """
        Returns a formatted Content-Type header string representation.

        This method reconstructs the Content-Type header string from the object's
        properties, including the media type and any defined parameters (charset, name).

        :returns: Properly formatted Content-Type header string.
        """
        return_string = self.MediaType
        if self.Charset != str():
            return_string = f"{return_string}; charset={self.Charset}"
        if self.Name != str():
            return_string = f"{return_string}; name={self.Name}"
        return return_string
