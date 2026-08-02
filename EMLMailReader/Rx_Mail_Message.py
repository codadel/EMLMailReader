import json
import os
from .Mail_Address import MailAddress, MailAddressCollection
from .Mail_Attachment import MailAttachmentCollection
from .Content_Type import ContentType
from .Content_Disposition import ContentDisposition
from .Enumerations import TransferEncoding, EntityType
from .Custom_Exceptions import FolderNotAvailableError


class RxMailMessage:
    """
    Comprehensive representation of a parsed email message and its MIME structure.

    This class encapsulates all information extracted from an EML file including headers,
    body content, attachments, and MIME metadata. It supports both simple and complex
    multipart email structures with full hierarchical representation of nested MIME parts.
    """
    def __init__(self):
        self.From = None
        """Sender's email address from the 'From' header."""
        self.To = MailAddressCollection()
        """Collection of recipient email addresses from the 'To' header."""
        self.Cc = MailAddressCollection()
        """Collection of carbon copy recipient addresses from the 'Cc' header."""
        self.Bcc = MailAddressCollection()
        """Collection of blind carbon copy recipient addresses from the 'Bcc' header."""
        self.ReplyTo = MailAddressCollection()
        """Collection of reply-to addresses from the 'Reply-To' header."""
        self.Subject = str()
        """Email subject line with decoded content."""
        self.Body = str()
        """Decoded text content of the email body."""
        self.ContentType = None
        """MIME Content-Type information for this message part."""
        self.ContentDisposition = None
        """MIME Content-Disposition information for this message part."""
        self.ContentTransferEncoding = TransferEncoding.SEVEN_BIT
        """Transfer encoding method used for this message part content."""
        self.Headers = dict()
        """Dictionary of additional headers not handled by specific properties."""
        self.MessageID = str()
        """Unique message identifier from the 'Message-ID' header."""
        self.IsMultiPart = False
        """Indicates whether this message contains multiple MIME parts."""
        self.MimeVersion = str()
        """MIME version specification from the 'MIME-Version' header."""
        self.Date = str()
        """Date and time when the message was sent from the 'Date' header."""
        self.Children = list()
        """List of child MIME parts for multipart messages."""
        self.ContentDescription = str()
        """Textual description of the content from 'Content-Description' header."""
        self.EntityType = EntityType.MIME_PART
        """Classification of this MIME entity (text, attachment, or container)."""
        self.Attachments = MailAttachmentCollection()
        """Collection of all file attachments found in this message."""
        self.ContentID = str()
        """Unique content identifier for referencing this part from 'Content-ID' header."""

    def add_mail_address(self, PropertyName: str, MailAddressValue: str):
        """
        [INTERNAL USE ONLY] Parses and adds an email address to the specified recipient collection.

        This method is used during EML parsing to populate recipient lists (To, Cc, Bcc, ReplyTo)
        from header values. It handles address parsing and adds to the appropriate collection.

        :param PropertyName: Name of the recipient property ("To", "Cc", "Bcc", "ReplyTo").
        :param MailAddressValue: Raw email address string to parse and add.
        :returns: None - modifies the appropriate address collection.
        """
        mail_address = MailAddress()
        mail_address.parse(MailAddressValue)
        if PropertyName == "To":
            self.To.append(mail_address)
        elif PropertyName == "Cc":
            self.Cc.append(mail_address)
        elif PropertyName == "Bcc":
            self.Bcc.append(mail_address)
        elif PropertyName == "ReplyTo":
            self.ReplyTo.append(mail_address)
        else:
            raise Exception(f"{PropertyName} is not of type 'MailAddress'")

    def set_content_type(self, ContentTypeValue: str):
        """
        [INTERNAL USE ONLY] Parses and sets the Content-Type header for this MIME part.

        This method creates a ContentType object from the header string and assigns it
        to this message part. Used during EML parsing to process Content-Type headers.

        :param ContentTypeValue: Raw Content-Type header string to parse.
        :returns: None - sets the ContentType property of this message.
        """
        self.ContentType = ContentType()
        self.ContentType.parse(ContentTypeValue)

    def set_content_disposition(self, ContentDispositionValue: str):
        """
        [INTERNAL USE ONLY] Parses and sets the Content-Disposition header for this MIME part.

        This method creates a ContentDisposition object from the header string and assigns it
        to this message part. Used during EML parsing to process Content-Disposition headers.

        :param ContentDispositionValue: Raw Content-Disposition header string to parse.
        :returns: None - sets the ContentDisposition property of this message.
        """
        self.ContentDisposition = ContentDisposition()
        self.ContentDisposition.parse(ContentDispositionValue)

    def set_content_transfer_encoding(self, ContentTransferEncodingValue: str):
        """
        [INTERNAL USE ONLY] Parses and sets the Content-Transfer-Encoding for this MIME part.

        This method converts the header string to the appropriate TransferEncoding enum value.
        Defaults to 7-bit encoding for unrecognized values. Used during EML parsing.

        :param ContentTransferEncodingValue: Raw Content-Transfer-Encoding header string.
        :returns: None - sets the ContentTransferEncoding property of this message.
        """
        ContentTransferEncodingValue = ContentTransferEncodingValue.lower()
        if ContentTransferEncodingValue == "8bit":
            self.ContentTransferEncoding = TransferEncoding.EIGHT_BIT
        elif ContentTransferEncodingValue == "base64":
            self.ContentTransferEncoding = TransferEncoding.BASE64
        elif ContentTransferEncodingValue == "quoted-printable":
            self.ContentTransferEncoding = TransferEncoding.QUOTED_PRINTABLE
        else:
            self.ContentTransferEncoding = TransferEncoding.SEVEN_BIT

    def set_entity_type(self):
        """
        [INTERNAL USE ONLY] Determines and sets the entity type based on the Content-Type.

        This method classifies the MIME part as ATTACHMENT (binary files), TEXT (readable content),
        or MIME_PART (multipart container) based on the media type. Used during parsing to
        facilitate proper content handling.

        :returns: None - sets the EntityType property of this message.
        """
        media_type = self.ContentType.MediaType.lower()
        if media_type.startswith("application") or media_type.startswith("image"):
            self.EntityType = EntityType.ATTACHMENT
        elif media_type.startswith("multipart"):
            self.EntityType = EntityType.MIME_PART
        else:
            self.EntityType = EntityType.TEXT

    def export_as_json(self) -> str:
        """
        Converts the email message to a JSON string representation.

        This method serializes key message properties into a JSON format suitable for
        logging, debugging, or data exchange. Includes essential headers, metadata,
        and attachment count but excludes binary content and body text.

        :returns: JSON string containing structured representation of the message.
        """
        final_object = dict()
        final_object.update({
            "From": str(self.From),
            "Subject": self.Subject,
            "Message-ID": self.MessageID,
            "IsMultiPart": self.IsMultiPart,
            "Mime-Version": self.MimeVersion,
            "Date": self.Date,
            "Headers": self.Headers,
            "Content-Type": str(self.ContentType),
            "To": str(self.To),
            "Cc": str(self.Cc),
            "Bcc": str(self.Bcc),
            "Reply-To": str(self.ReplyTo),
            "Attachment-Count": self.Attachments.length()
        })

        return json.dumps(final_object)

    def save_attachments(self, TargetFolderPath: str):
        """
        Saves all email attachments to the specified directory.

        This method extracts and writes all attachment files to disk using their
        original filenames. If the target directory doesn't exist, an exception is raised.
        Existing files with the same names will be overwritten.

        :param TargetFolderPath: Directory path where attachment files should be saved.
        :returns: None - creates files in the specified directory.
        :raises FolderNotAvailableError: If the target directory doesn't exist.
        """
        if os.path.exists(TargetFolderPath):
            for attachment in self.Attachments.export_as_list():
                TargetFilePath = os.path.join(TargetFolderPath, attachment.Name)
                with open(TargetFilePath, "wb") as my_file:
                    my_file.write(attachment.Contents)
        else:
            raise FolderNotAvailableError(TargetFolderPath)
