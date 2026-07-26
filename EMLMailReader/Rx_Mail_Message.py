import json
import os

from .Content_Type import ContentType
from .Mail_Address import AddressList
from .Standards import HeaderCollection, TransferEncodingValue
from .Custom_Exceptions import FolderNotAvailableError


class RxMailMessage:
    """One parsed Internet message or MIME entity.

    Version 2 exposes one canonical representation for every field.  The same
    class represents the root message and every node in its MIME tree.
    """

    def __init__(self):
        self.Headers = HeaderCollection()
        self.From = AddressList()
        self.Sender = AddressList()
        self.ReplyTo = AddressList()
        self.To = AddressList()
        self.Cc = AddressList()
        self.Bcc = AddressList()
        self.Subject = ""
        self.Date = None
        self.MessageID = None
        self.InReplyTo = []
        self.References = []
        self.Comments = []
        self.Keywords = []
        self.Received = []
        self.ReturnPath = ""
        self.ResentBlocks = []
        self.TraceBlocks = []

        self.ContentType = ContentType()
        self.ContentDisposition = None
        self.ContentTransferEncoding = TransferEncodingValue.parse("7bit")
        self.MimeVersion = ""
        self.ContentDescription = ""
        self.ContentID = None
        self.MessagePartial = None
        self.ExternalBodyAccess = None

        self.RawSource = bytes()
        self.RawBody = bytes()
        self.DecodedBody = bytes()
        self._DecodedText = ""
        self.Children = []
        self.Preamble = ""
        self.Epilogue = ""
        self.Diagnostics = []

    @property
    def IsMultiPart(self) -> bool:
        return bool(self.Children) or self.ContentType.MediaType.startswith("multipart/")

    @property
    def Body(self) -> str:
        if not self.Children:
            return self._DecodedText
        candidates = [child.Body for child in self.Children if child.Body]
        if not candidates:
            return ""
        if self.ContentType.MediaType == "multipart/alternative":
            return candidates[-1]
        return candidates[0]

    @property
    def TextBody(self) -> str:
        if not self.Children:
            return self._DecodedText if self.ContentType.MediaType == "text/plain" else ""
        return next((child.TextBody for child in self.Children if child.TextBody), "")

    @property
    def HtmlBody(self) -> str:
        if not self.Children:
            return self._DecodedText if self.ContentType.MediaType == "text/html" else ""
        return next((child.HtmlBody for child in self.Children if child.HtmlBody), "")

    @property
    def Name(self) -> str:
        if self.ContentDisposition and self.ContentDisposition.FileName:
            return self.ContentDisposition.FileName
        return self.ContentType.Name

    @property
    def IsInline(self) -> bool:
        return bool(self.ContentDisposition and self.ContentDisposition.DispositionType == "inline")

    @property
    def IsAttachment(self) -> bool:
        disposition = self.ContentDisposition.DispositionType if self.ContentDisposition else ""
        return disposition == "attachment" or (bool(self.Name) and disposition != "inline")

    @property
    def Attachments(self) -> tuple["RxMailMessage", ...]:
        attachments = [self] if self.IsAttachment else []
        for child in self.Children:
            attachments.extend(child.Attachments)
        return tuple(attachments)

    @property
    def InlineResources(self) -> tuple["RxMailMessage", ...]:
        resources = [self] if self.IsInline else []
        for child in self.Children:
            resources.extend(child.InlineResources)
        return tuple(resources)

    def export_as_json(self) -> str:
        """Serialize the sole version 2 structured schema."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self) -> dict:
        """Return the complete structured version 2 schema."""
        return {
            "schema_version": 2,
            "headers": self.Headers.to_list(),
            "from": self.From.to_dict(),
            "sender": self.Sender.to_dict(),
            "reply_to": self.ReplyTo.to_dict(),
            "to": self.To.to_dict(),
            "cc": self.Cc.to_dict(),
            "bcc": self.Bcc.to_dict(),
            "subject": self.Subject,
            "date": self.Date.to_dict() if self.Date else None,
            "message_id": self.MessageID.to_dict() if self.MessageID else None,
            "in_reply_to": [value.to_dict() for value in self.InReplyTo],
            "references": [value.to_dict() for value in self.References],
            "comments": list(self.Comments),
            "keywords": list(self.Keywords),
            "return_path": self.ReturnPath,
            "received": list(self.Received),
            "resent_blocks": [block.to_dict() for block in self.ResentBlocks],
            "trace_blocks": [block.to_dict() for block in self.TraceBlocks],
            "mime_version": self.MimeVersion,
            "content_type": self.ContentType.to_dict(),
            "content_disposition": self.ContentDisposition.to_dict() if self.ContentDisposition else None,
            "content_transfer_encoding": self.ContentTransferEncoding.to_dict(),
            "content_id": self.ContentID.to_dict() if self.ContentID else None,
            "content_description": self.ContentDescription,
            "message_partial": self.MessagePartial.to_dict() if self.MessagePartial else None,
            "external_body_access": self.ExternalBodyAccess.to_dict() if self.ExternalBodyAccess else None,
            "is_multipart": self.IsMultiPart,
            "is_attachment": self.IsAttachment,
            "is_inline": self.IsInline,
            "name": self.Name,
            "preamble": self.Preamble,
            "epilogue": self.Epilogue,
            "body": self.Body,
            "text_body": self.TextBody,
            "html_body": self.HtmlBody,
            "children": [child.to_dict() for child in self.Children],
            "diagnostics": [item.to_dict() for item in self.Diagnostics],
        }

    def save_attachments(self, TargetFolderPath: str):
        """Save all attachment MIME parts to an existing directory."""
        if not os.path.isdir(TargetFolderPath):
            raise FolderNotAvailableError(TargetFolderPath)
        for attachment in self.Attachments:
            safe_name = os.path.basename(attachment.Name)
            if safe_name in ("", ".", ".."):
                safe_name = "attachment"
            payload = attachment.DecodedBody
            if not payload and attachment.Children:
                payload = attachment.Children[0].RawSource
            with open(os.path.join(TargetFolderPath, safe_name), "wb") as target:
                target.write(payload)
