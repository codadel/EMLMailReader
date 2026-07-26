from email.message import Message
from email.policy import default


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
        self.Parameters = dict()
        """All decoded MIME parameters, including RFC 2231 extensions."""
        self.RawValue = str()
        self.IsExplicit = False

    def parse(self, ContentTypeString: str | None = None, *, effective_media_type: str | None = None):
        """
        Parses a Content-Type header string and populates the object's properties.

        This method extracts the media type and associated parameters (charset, boundary, name)
        from the header string. If no Content-Type is provided or it's invalid, defaults to
        'text/plain;charset=us-ascii' as specified in RFC 2045.

        :param ContentTypeString: The Content-Type header value to parse.
        :returns: None - modifies the object's properties in place.
        """
        raw_value = (ContentTypeString or "").strip()
        value = raw_value or (effective_media_type or "text/plain")
        self.RawValue = raw_value
        self.IsExplicit = bool(raw_value)
        message = Message(policy=default)
        message["Content-Type"] = value
        self.MediaType = message.get_content_type().lower()
        parameters = message.get_params(header="content-type", failobj=[])[1:]
        self.Parameters = {str(key).lower(): str(parameter) for key, parameter in parameters}
        self.Charset = (message.get_content_charset() or "us-ascii").lower()
        self.Boundary = message.get_boundary() or ""
        self.Name = self.Parameters.get("name", "")

    def get_parameter(self, name: str, default=None):
        return self.Parameters.get(name.lower(), default)

    def to_header_value(self) -> str:
        """Return an RFC-compliant value including all parameters."""
        message = Message(policy=default)
        message["Content-Type"] = self.RawValue or self.MediaType
        return str(message["Content-Type"])

    def __str__(self) -> str:
        """
        Returns a formatted Content-Type header string representation.

        This method reconstructs the Content-Type header string from the object's
        properties, including the media type and any defined parameters (charset, name).

        :returns: Properly formatted Content-Type header string.
        """
        return self.to_header_value()

    def to_dict(self) -> dict:
        return {
            "media_type": self.MediaType,
            "charset": self.Charset,
            "boundary": self.Boundary,
            "name": self.Name,
            "parameters": dict(self.Parameters),
            "raw_value": self.RawValue,
            "is_explicit": self.IsExplicit,
        }
