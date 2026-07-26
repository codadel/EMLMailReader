"""Structured representation of a MIME Content-Disposition field."""

from email.message import Message
from email.policy import default
from email.utils import parsedate_to_datetime
from typing import TypeVar

from .Standards import JsonObject, ParsedDateTime

_DefaultT = TypeVar("_DefaultT")


class ContentDisposition:
    """Represent a parsed MIME Content-Disposition field.

    The model retains the original field value and every decoded parameter while
    exposing common RFC 2183 metadata such as the filename, size, and lifecycle
    dates through dedicated attributes.

    Attributes:
        DispositionType: Lowercase registered or extension disposition token.
        FileName: Suggested filename decoded from the ``filename`` parameter.
        CreationDate: Parsed ``creation-date`` value, if present.
        ModificationDate: Parsed ``modification-date`` value, if present.
        ReadDate: Parsed ``read-date`` value, if present.
        Size: Declared content size in bytes, or zero when absent or invalid.
        Parameters: All decoded parameters keyed by lowercase name.
        RawValue: Original Content-Disposition field value.
        IsExplicit: Whether the source contained a Content-Disposition field.
    """

    def __init__(self) -> None:
        """Initialize an empty, non-explicit disposition value."""
        self.DispositionType = ""
        """The registered or extension disposition token."""
        self.FileName = ""
        """The suggested filename for the MIME entity when saved to disk."""
        self.CreationDate: ParsedDateTime | None = None
        """RFC 2822 formatted date when the MIME entity was originally created."""
        self.ModificationDate: ParsedDateTime | None = None
        """RFC 2822 formatted date when the MIME entity was last modified."""
        self.Size = 0
        """Size of the MIME entity content in bytes."""
        self.ReadDate: ParsedDateTime | None = None
        self.Parameters: dict[str, str] = {}
        self.RawValue = ""
        self.IsExplicit = False

    def parse(self, ContentDispositionString: str) -> None:
        """Parse a field value and replace this instance's disposition metadata.

        Args:
            ContentDispositionString: Content-Disposition value without the
                field name.
        """
        value = (ContentDispositionString or "").strip()
        self.DispositionType = ""
        self.RawValue = value
        self.IsExplicit = bool(value)
        message = Message(policy=default)
        message["Content-Disposition"] = value
        disposition = (
            message.get_content_disposition() or value.split(";", 1)[0]
        ).lower()
        self.DispositionType = disposition
        parameters = message.get_params(header="content-disposition", failobj=[])[1:]
        self.Parameters = {
            str(key).lower(): str(parameter) for key, parameter in parameters
        }
        self.FileName = message.get_filename() or self.Parameters.get("filename", "")
        self.CreationDate = self._parse_date(self.Parameters.get("creation-date", ""))
        self.ModificationDate = self._parse_date(
            self.Parameters.get("modification-date", "")
        )
        self.ReadDate = self._parse_date(self.Parameters.get("read-date", ""))
        size = self.Parameters.get("size", "")
        self.Size = int(size) if size.isdigit() else 0

    def get_parameter(
        self, name: str, default: _DefaultT | None = None
    ) -> str | _DefaultT | None:
        """Return a decoded parameter by case-insensitive name.

        Args:
            name: Parameter name to look up.
            default: Value returned when the parameter is absent.
        """
        return self.Parameters.get(name.lower(), default)

    @staticmethod
    def _parse_date(value: str) -> ParsedDateTime | None:
        """Convert an RFC-style disposition date into a lossless typed value."""
        if not value:
            return None
        try:
            return ParsedDateTime(value, parsedate_to_datetime(value), True)
        except (TypeError, ValueError, OverflowError):
            return ParsedDateTime(value, None, False)

    def to_header_value(self) -> str:
        """Return the normalized Content-Disposition value for a header field."""
        message = Message(policy=default)
        message["Content-Disposition"] = self.RawValue or self.DispositionType
        return str(message["Content-Disposition"])

    def __str__(self) -> str:
        """Return the normalized Content-Disposition field value."""
        return self.to_header_value()

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible representation of the disposition metadata."""
        return {
            "type": self.DispositionType,
            "filename": self.FileName,
            "creation_date": self.CreationDate.to_dict() if self.CreationDate else None,
            "modification_date": self.ModificationDate.to_dict()
            if self.ModificationDate
            else None,
            "read_date": self.ReadDate.to_dict() if self.ReadDate else None,
            "size": self.Size,
            "parameters": dict(self.Parameters),
            "raw_value": self.RawValue,
            "is_explicit": self.IsExplicit,
        }
