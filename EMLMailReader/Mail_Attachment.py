from .Content_Type import ContentType
from .Content_Disposition import ContentDisposition
from copy import deepcopy


class MailAttachment:
    """
    Represents a file attachment found in an email message.

    This class encapsulates all information about an email attachment including
    its content, metadata, and MIME properties required for proper handling and extraction.
    """
    def __init__(self):
        self.Name = str()
        """The filename of the attachment as it should appear when saved."""
        self.ContentType = ContentType()
        """MIME Content-Type information including media type and parameters."""
        self.ContentDisposition = ContentDisposition()
        """Content-Disposition header information including disposition type and metadata."""
        self.Contents = bytes()
        """The actual binary content of the attachment file."""
        self.ContentID = str()
        """Unique identifier for the attachment, used for referencing in HTML content."""

    def parse_values(self, contents: bytes, content_type: ContentType, content_disposition: ContentDisposition, content_id: str):
        """
        Initializes the MailAttachment object with provided content and metadata.

        This method populates all attachment properties and determines the appropriate
        filename from either the Content-Type name parameter or Content-Disposition filename.

        :param contents: Binary content of the attachment file.
        :param content_type: Parsed Content-Type header information.
        :param content_disposition: Parsed Content-Disposition header information.
        :param content_id: Content-ID value for referencing the attachment.
        :returns: None - modifies the object's properties in place.
        """
        self.Contents = deepcopy(contents)
        self.ContentType = deepcopy(content_type)
        self.ContentDisposition = deepcopy(content_disposition)
        self.ContentID = deepcopy(content_id)
        if self.ContentType.Name != str():
            self.Name = self.ContentType.Name
        elif self.ContentDisposition.FileName != str():
            self.Name = self.ContentDisposition.FileName
        else:
            self.Name = str()


class MailAttachmentCollection:
    """
    A collection class to manage multiple MailAttachment instances.

    This class provides a container for storing and manipulating lists of email attachments
    found within an email message, facilitating batch operations and iteration.
    """
    def __init__(self):
        self.__attachments = list[MailAttachment]()
        """Private list containing MailAttachment instances in the collection."""

    def append(self, attachment: MailAttachment):
        """
        Adds a MailAttachment instance to the end of the collection.

        :param attachment: MailAttachment object to be added to the collection.
        :returns: None - modifies the collection in place.
        """
        self.__attachments.append(attachment)

    def length(self) -> int:
        """
        Returns the number of MailAttachment items in the collection.

        :returns: Integer count of MailAttachment instances in the collection.
        """
        return len(self.__attachments)

    def export_as_list(self) -> list:
        """
        Exports the collection as a new list of MailAttachment instances.

        This method creates a deep copy of the internal collection to prevent
        external modification of the collection's internal state.

        :returns: A new list containing deep copies of all MailAttachment instances.
        """
        return deepcopy(self.__attachments)
