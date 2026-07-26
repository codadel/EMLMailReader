from email.message import Message
from email.policy import default
from email.utils import parsedate_to_datetime
from .Standards import ParsedDateTime


class ContentDisposition:
    """
    A class to represent the Content-Disposition header of a MIME entity.

    This class parses and stores information from the Content-Disposition header,
    which indicates how content should be presented (as attachment or inline)
    and includes metadata such as filename, dates, and size.
    """
    def __init__(self):
        self.DispositionType = ""
        """The registered or extension disposition token."""
        self.FileName = ""
        """The suggested filename for the MIME entity when saved to disk."""
        self.CreationDate = None
        """RFC 2822 formatted date when the MIME entity was originally created."""
        self.ModificationDate = None
        """RFC 2822 formatted date when the MIME entity was last modified."""
        self.Size = 0
        """Size of the MIME entity content in bytes."""
        self.ReadDate = None
        self.Parameters = dict()
        self.RawValue = ""
        self.IsExplicit = False

    def parse(self, ContentDispositionString: str):
        """
        Parses a Content-Disposition header string and populates the object's properties.

        This method extracts disposition type (inline/attachment) and associated parameters
        like filename, size, creation-date, and modification-date from the header string.

        :param ContentDispositionString: The Content-Disposition header value to parse.
        :returns: None - modifies the object's properties in place.
        """
        value = (ContentDispositionString or "").strip()
        self.DispositionType = ""
        self.RawValue = value
        self.IsExplicit = bool(value)
        message = Message(policy=default)
        message["Content-Disposition"] = value
        disposition = (message.get_content_disposition() or value.split(";", 1)[0]).lower()
        self.DispositionType = disposition
        parameters = message.get_params(header="content-disposition", failobj=[])[1:]
        self.Parameters = {str(key).lower(): str(parameter) for key, parameter in parameters}
        self.FileName = message.get_filename() or self.Parameters.get("filename", "")
        self.CreationDate = self._parse_date(self.Parameters.get("creation-date", ""))
        self.ModificationDate = self._parse_date(self.Parameters.get("modification-date", ""))
        self.ReadDate = self._parse_date(self.Parameters.get("read-date", ""))
        size = self.Parameters.get("size", "")
        self.Size = int(size) if size.isdigit() else 0

    def get_parameter(self, name: str, default=None):
        return self.Parameters.get(name.lower(), default)

    @staticmethod
    def _parse_date(value: str):
        if not value:
            return None
        try:
            return ParsedDateTime(value, parsedate_to_datetime(value), True)
        except (TypeError, ValueError, OverflowError):
            return ParsedDateTime(value, None, False)

    def to_header_value(self) -> str:
        message = Message(policy=default)
        message["Content-Disposition"] = self.RawValue or self.DispositionType
        return str(message["Content-Disposition"])

    def __str__(self) -> str:
        """Return the normalized RFC header value."""
        return self.to_header_value()

    def to_dict(self) -> dict:
        return {
            "type": self.DispositionType,
            "filename": self.FileName,
            "creation_date": self.CreationDate.to_dict() if self.CreationDate else None,
            "modification_date": self.ModificationDate.to_dict() if self.ModificationDate else None,
            "read_date": self.ReadDate.to_dict() if self.ReadDate else None,
            "size": self.Size,
            "parameters": dict(self.Parameters),
            "raw_value": self.RawValue,
            "is_explicit": self.IsExplicit,
        }
