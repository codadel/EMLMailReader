"""Canonical Internet-message and MIME-entity model."""

import json
import os

from .Content_Disposition import ContentDisposition
from .Content_Type import ContentType
from .Custom_Exceptions import FolderNotAvailableError
from .Mail_Address import AddressList
from .Standards import (
    ExternalBodyAccessInfo,
    HeaderCollection,
    JsonObject,
    MessagePartialInfo,
    ParsedDateTime,
    ParseDiagnostic,
    ParsedMessageID,
    ResentBlock,
    TraceBlock,
    TransferEncodingValue,
)


class RxMailMessage:
    """Represent one parsed Internet message or MIME entity.

    The same class is used for the root message and every node in its recursive
    MIME tree. Internet-message fields, MIME metadata, source bytes, decoded
    bodies, child entities, and parser diagnostics therefore remain available
    through one canonical model.

    Attributes:
        Headers: Ordered, duplicate-preserving header collection.
        From: Structured originator address list.
        Sender: Structured sender address list.
        ReplyTo: Structured Reply-To address list.
        To: Structured primary-recipient address list.
        Cc: Structured carbon-copy address list.
        Bcc: Structured blind-copy address list.
        Subject: Decoded Subject field value.
        Date: Structured parsed Date value or ``None``.
        MessageID: Structured Message-ID value or ``None``.
        InReplyTo: Parsed identifiers from the In-Reply-To field.
        References: Parsed identifiers from the References field.
        Comments: Decoded Comments field values in source order.
        Keywords: Decoded Keywords field values in source order.
        Received: Unfolded Received values in source order.
        ReturnPath: Unfolded Return-Path value.
        ResentBlocks: Contiguous structured Resent field groups.
        TraceBlocks: Structured Return-Path and Received groups.
        ContentType: Effective and source MIME content type.
        ContentDisposition: Parsed disposition or ``None``.
        ContentTransferEncoding: Lossless transfer-encoding value.
        MimeVersion: Unfolded MIME-Version field value.
        ContentDescription: Decoded Content-Description value.
        ContentID: Structured Content-ID value or ``None``.
        MessagePartial: ``message/partial`` metadata or ``None``.
        ExternalBodyAccess: ``message/external-body`` metadata or ``None``.
        RawSource: Source bytes for this entity; exact input bytes at the root.
        RawBody: Body bytes before content-transfer decoding.
        DecodedBody: Transfer-decoded leaf payload bytes.
        Children: Direct child MIME entities.
        Preamble: Text preceding the first multipart boundary.
        Epilogue: Text following the closing multipart boundary.
        Diagnostics: Standards findings attached to this entity.
    """

    def __init__(self) -> None:
        """Initialize an empty message using RFC/MIME default field values."""
        self.Headers = HeaderCollection()
        self.From = AddressList()
        self.Sender = AddressList()
        self.ReplyTo = AddressList()
        self.To = AddressList()
        self.Cc = AddressList()
        self.Bcc = AddressList()
        self.Subject = ""
        self.Date: ParsedDateTime | None = None
        self.MessageID: ParsedMessageID | None = None
        self.InReplyTo: list[ParsedMessageID] = []
        self.References: list[ParsedMessageID] = []
        self.Comments: list[str] = []
        self.Keywords: list[str] = []
        self.Received: list[str] = []
        self.ReturnPath = ""
        self.ResentBlocks: list[ResentBlock] = []
        self.TraceBlocks: list[TraceBlock] = []

        self.ContentType = ContentType()
        self.ContentDisposition: ContentDisposition | None = None
        self.ContentTransferEncoding = TransferEncodingValue.parse("7bit")
        self.MimeVersion = ""
        self.ContentDescription = ""
        self.ContentID: ParsedMessageID | None = None
        self.MessagePartial: MessagePartialInfo | None = None
        self.ExternalBodyAccess: ExternalBodyAccessInfo | None = None

        self.RawSource = b""
        self.RawBody = b""
        self.DecodedBody = b""
        self._DecodedText = ""
        self.Children: list[RxMailMessage] = []
        self.Preamble = ""
        self.Epilogue = ""
        self.Diagnostics: list[ParseDiagnostic] = []

    @property
    def IsMultiPart(self) -> bool:
        """Return whether the entity is a multipart container or has children."""
        return bool(self.Children) or self.ContentType.MediaType.startswith(
            "multipart/"
        )

    @property
    def Body(self) -> str:
        """Return the preferred decoded text for this MIME subtree.

        Leaves return their decoded text. ``multipart/alternative`` chooses its
        last non-empty alternative; other containers choose the first non-empty
        child body.
        """
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
        """Return the first decoded ``text/plain`` body in this subtree."""
        if not self.Children:
            return (
                self._DecodedText if self.ContentType.MediaType == "text/plain" else ""
            )
        return next((child.TextBody for child in self.Children if child.TextBody), "")

    @property
    def HtmlBody(self) -> str:
        """Return the first decoded ``text/html`` body in this subtree."""
        if not self.Children:
            return (
                self._DecodedText if self.ContentType.MediaType == "text/html" else ""
            )
        return next((child.HtmlBody for child in self.Children if child.HtmlBody), "")

    @property
    def Name(self) -> str:
        """Return the disposition filename or fallback Content-Type name."""
        if self.ContentDisposition and self.ContentDisposition.FileName:
            return self.ContentDisposition.FileName
        return self.ContentType.Name

    @property
    def IsInline(self) -> bool:
        """Return whether the entity has an explicit inline disposition."""
        return bool(
            self.ContentDisposition
            and self.ContentDisposition.DispositionType == "inline"
        )

    @property
    def IsAttachment(self) -> bool:
        """Return whether the entity should be exposed as an attachment.

        Explicit attachment dispositions qualify. A named entity also qualifies
        unless it is explicitly inline.
        """
        disposition = (
            self.ContentDisposition.DispositionType if self.ContentDisposition else ""
        )
        return disposition == "attachment" or (
            bool(self.Name) and disposition != "inline"
        )

    @property
    def Attachments(self) -> tuple["RxMailMessage", ...]:
        """Return attachment entities in this subtree as an immutable tuple."""
        attachments: list[RxMailMessage] = [self] if self.IsAttachment else []
        for child in self.Children:
            attachments.extend(child.Attachments)
        return tuple(attachments)

    @property
    def InlineResources(self) -> tuple["RxMailMessage", ...]:
        """Return explicitly inline entities in this subtree as an immutable tuple."""
        resources: list[RxMailMessage] = [self] if self.IsInline else []
        for child in self.Children:
            resources.extend(child.InlineResources)
        return tuple(resources)

    def export_as_json(self) -> str:
        """Serialize the canonical recursive schema as Unicode-preserving JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self) -> JsonObject:
        """Return the complete JSON-compatible canonical message schema.

        Source and decoded byte payloads are intentionally omitted. Attachment
        and inline-resource views are not duplicated because those entities
        already appear recursively under ``children``.
        """
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
            "content_disposition": self.ContentDisposition.to_dict()
            if self.ContentDisposition
            else None,
            "content_transfer_encoding": self.ContentTransferEncoding.to_dict(),
            "content_id": self.ContentID.to_dict() if self.ContentID else None,
            "content_description": self.ContentDescription,
            "message_partial": self.MessagePartial.to_dict()
            if self.MessagePartial
            else None,
            "external_body_access": self.ExternalBodyAccess.to_dict()
            if self.ExternalBodyAccess
            else None,
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

    def save_attachments(self, TargetFolderPath: str) -> None:
        """Write every attachment payload in this subtree to a directory.

        Filenames are reduced to their basename; empty or unsafe basename-only
        values use ``attachment``. Existing files with the same name are
        overwritten.

        Args:
            TargetFolderPath: Existing destination directory.

        Raises:
            FolderNotAvailableError: If the destination directory is missing.
        """
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
