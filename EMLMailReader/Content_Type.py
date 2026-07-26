"""Structured representation of a MIME Content-Type field."""

from email.message import Message
from email.policy import default


class ContentType:
    """Represent the effective and source MIME content type for one entity.

    The class preserves whether Content-Type was explicit, retains all decoded
    parameters, and exposes frequently used MIME values as dedicated
    attributes.

    Attributes:
        MediaType: Effective lowercase ``type/subtype`` value.
        Charset: Declared text charset, defaulting to MIME US-ASCII.
        Boundary: Multipart boundary or an empty string.
        Name: Suggested content name from the ``name`` parameter.
        Parameters: All decoded parameters keyed by lowercase name.
        RawValue: Original Content-Type field value, excluding the field name.
        IsExplicit: Whether the source contained a Content-Type field.
    """

    def __init__(self):
        """Initialize the RFC 2045 default ``text/plain; charset=us-ascii``."""
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
        """Parse a Content-Type value and replace this instance's metadata.

        Args:
            ContentTypeString: Source field value, or ``None`` when omitted.
            effective_media_type: Media type inferred by the MIME parser when
                no explicit field exists. Defaults to ``text/plain``.
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
        """Return a decoded parameter by case-insensitive name."""
        return self.Parameters.get(name.lower(), default)

    def to_header_value(self) -> str:
        """Return the normalized Content-Type value including its parameters."""
        message = Message(policy=default)
        message["Content-Type"] = self.RawValue or self.MediaType
        return str(message["Content-Type"])

    def __str__(self) -> str:
        """Return the normalized Content-Type field value."""
        return self.to_header_value()

    def to_dict(self) -> dict:
        """Return a JSON-compatible representation of the content type."""
        return {
            "media_type": self.MediaType,
            "charset": self.Charset,
            "boundary": self.Boundary,
            "name": self.Name,
            "parameters": dict(self.Parameters),
            "raw_value": self.RawValue,
            "is_explicit": self.IsExplicit,
        }
