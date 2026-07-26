"""RFC 5322 + RFC 6854 + MIME + RFC 6532 parsing engine."""

from __future__ import annotations

import re
from base64 import b64decode
from email import policy
from email.message import Message
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from quopri import decodestring as decode_quoted_printable

from .Content_Disposition import ContentDisposition
from .Content_Type import ContentType
from .Enumerations import TransferEncoding
from .Mail_Address import AddressList
from .Rx_Mail_Message import RxMailMessage
from .Standards import (
    AddressGroup,
    DiagnosticSeverity,
    ExternalBodyAccessInfo,
    HeaderCollection,
    HeaderField,
    MessagePartialInfo,
    ParsedDateTime,
    ParseDiagnostic,
    ParsedMessageID,
    ParserLimits,
    ParsingMode,
    ResentBlock,
    StandardsComplianceError,
    SyntaxStatus,
    TraceBlock,
    TransferEncodingValue,
)

_ADDRESS_HEADERS = {
    "from",
    "sender",
    "reply-to",
    "to",
    "cc",
    "bcc",
    "resent-from",
    "resent-sender",
    "resent-to",
    "resent-cc",
    "resent-bcc",
}
_RESENT_HEADERS = {
    "resent-date",
    "resent-from",
    "resent-sender",
    "resent-to",
    "resent-cc",
    "resent-bcc",
    "resent-message-id",
}
_MSG_ID = re.compile(r"^\s*<([^<>@\s]+)@([^<>\s]+)>\s*$", re.DOTALL)
_MSG_IDS = re.compile(r"<[^<>]+@[^<>]+>")
_OBSOLETE_ROUTE = re.compile(r"(?:<\s*)?@[^\s,:>]+(?:\s*,\s*@[^\s,:>]+)*\s*:")
_IMF_SINGLETON_HEADERS = (
    "Date",
    "From",
    "Sender",
    "Reply-To",
    "To",
    "Cc",
    "Bcc",
    "Message-ID",
    "In-Reply-To",
    "References",
    "Subject",
    "MIME-Version",
)
_MIME_SINGLETON_HEADERS = (
    "Content-Type",
    "Content-Transfer-Encoding",
    "Content-Disposition",
    "Content-ID",
    "Content-Description",
)


def _mode(value: ParsingMode | str) -> ParsingMode:
    """Normalize an enum or string into a supported parser mode.

    Unknown values deliberately fall back to modern receiver behavior.
    """
    if isinstance(value, ParsingMode):
        return value
    try:
        return ParsingMode(str(value).lower())
    except ValueError:
        return ParsingMode.MODERN


class StandardsParser:
    """Build the canonical MIME tree and report standards diagnostics.

    The parser delegates syntax recovery to Python's email package, then
    preserves source-oriented header/body data, projects structured IMF and
    MIME values, validates the supported standards bundle, and enforces
    configured resource limits.
    """

    def __init__(
        self,
        parsing_mode: ParsingMode | str = ParsingMode.MODERN,
        limits: ParserLimits | None = None,
    ) -> None:
        """Configure parsing behavior and resource guards."""
        self.parsing_mode = _mode(parsing_mode)
        self.limits = limits or ParserLimits()
        self._part_count = 0

    def parse(self, source: bytes) -> RxMailMessage:
        """Parse complete Internet-message bytes into a canonical MIME tree.

        Args:
            source: Complete wire-format message bytes.

        Returns:
            Root message containing parsed fields, child MIME nodes, bodies, and
            diagnostics.

        Raises:
            StandardsComplianceError: If strict mode finds any error-level
                diagnostic in the root or a descendant.
        """
        self._part_count = 0
        message = BytesParser(policy=policy.default).parsebytes(source)
        result = self._convert(message, source=source, depth=0)
        result.Diagnostics[0:0] = self._source_diagnostics(source, result.Headers)
        self._validate_required(result)
        all_diagnostics = self._all_diagnostics(result)
        if self.parsing_mode == ParsingMode.STRICT and any(
            item.severity == DiagnosticSeverity.ERROR for item in all_diagnostics
        ):
            raise StandardsComplianceError(all_diagnostics)
        return result

    def _convert(
        self, part: Message, source: bytes | None, depth: int
    ) -> RxMailMessage:
        """Convert one native email entity and its descendants into the model.

        ``source`` is supplied only for the root so its exact octets can be
        retained; child source values are normalized native serializations.
        """
        result = RxMailMessage()
        part_source = (
            source if source is not None else part.as_bytes(policy=policy.default)
        )
        result.RawSource = part_source
        separator = re.search(rb"\r\n\r\n|\n\n|\r\r", part_source)
        result.RawBody = part_source[separator.end() :] if separator else b""
        self._part_count += 1
        if depth > self.limits.max_mime_depth:
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="MimeDepthLimitExceeded",
                    message=f"MIME nesting exceeds {self.limits.max_mime_depth}",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 2046",
                )
            )
            return result
        if self._part_count > self.limits.max_parts:
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="MimePartLimitExceeded",
                    message=f"MIME part count exceeds {self.limits.max_parts}",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 2046",
                )
            )
            return result
        result.Headers = self._headers(part)
        initial_defect_count = len(getattr(part, "defects", ()))
        result.Diagnostics.extend(self._defects(part))
        self._populate_imf(result, part)
        self._populate_mime(result, part)
        self._validate_entity_headers(result)

        result.Preamble = part.preamble or ""
        result.Epilogue = part.epilogue or ""
        native_children = self._native_children(result, part)

        if native_children or part.is_multipart():
            for native_child in native_children:
                if self._part_count >= self.limits.max_parts:
                    result.Diagnostics.append(
                        ParseDiagnostic(
                            code="MimePartLimitExceeded",
                            message=f"MIME part count exceeds {self.limits.max_parts}",
                            severity=DiagnosticSeverity.ERROR,
                            rfc="RFC 2046",
                        )
                    )
                    break
                child = self._convert(native_child, source=None, depth=depth + 1)
                result.Children.append(child)
        else:
            self._populate_leaf_body(result, part, top_level=source is not None)
            current_defects = self._defects(part)
            result.Diagnostics.extend(current_defects[initial_defect_count:])

        return result

    def _native_children(self, result: RxMailMessage, part: Message) -> list[Message]:
        """Return child entities, explicitly decoding encoded message/global.

        Python exposes most multipart and message children directly. RFC 6532
        ``message/global`` with Base64 or quoted-printable transfer encoding
        requires an additional decode-and-parse step.
        """
        payload = part.get_payload()
        children = (
            [item for item in payload if isinstance(item, Message)]
            if isinstance(payload, list)
            else []
        )
        media_type = part.get_content_type().lower()
        transfer_encoding = (
            (part.get("Content-Transfer-Encoding") or "7bit").strip().lower()
        )
        if media_type != "message/global" or transfer_encoding not in (
            "base64",
            "quoted-printable",
        ):
            return children
        try:
            encoded = children[0].get_payload() if children else payload
            if isinstance(encoded, str):
                encoded_bytes = encoded.encode("ascii")
            elif isinstance(encoded, bytes):
                encoded_bytes = encoded
            else:
                raise TypeError("message/global payload is not encoded text")
            if transfer_encoding == "base64":
                decoded = b64decode(encoded_bytes)
            else:
                decoded = decode_quoted_printable(encoded_bytes)
            return [BytesParser(policy=policy.default).parsebytes(decoded)]
        except (IndexError, TypeError, ValueError) as error:
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="InvalidMessageGlobalEncoding",
                    message=f"Could not decode message/global body: {error}",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 6532",
                    section="3.7",
                    header="Content-Transfer-Encoding",
                )
            )
            return children

    @classmethod
    def _all_diagnostics(cls, result: RxMailMessage) -> list[ParseDiagnostic]:
        """Flatten diagnostics from an entity and every descendant."""
        diagnostics = list(result.Diagnostics)
        for child in result.Children:
            diagnostics.extend(cls._all_diagnostics(child))
        return diagnostics

    def _headers(self, message: Message) -> HeaderCollection:
        """Build ordered lossless header occurrences from a native message."""
        fields = HeaderCollection()
        parsed_items = list(message.items())
        raw_items = list(message.raw_items())
        for index, (raw_name, raw_value) in enumerate(raw_items):
            parsed_value = (
                str(parsed_items[index][1]) if index < len(parsed_items) else raw_value
            )
            unfolded = re.sub(r"(?:\r\n|\n|\r)(?=[ \t])", "", raw_value)
            status = (
                SyntaxStatus.OBSOLETE
                if (
                    re.search(r"(?:\r\n|\n|\r)[ \t]+(?:\r\n|\n|\r)", raw_value)
                    or _OBSOLETE_ROUTE.search(raw_value)
                )
                else SyntaxStatus.CURRENT
            )
            fields.append(
                HeaderField(
                    name=raw_name,
                    raw_name=raw_name,
                    raw_value=raw_value,
                    unfolded_value=unfolded,
                    decoded_value=parsed_value,
                    index=index,
                    syntax_status=status,
                )
            )
        return fields

    def _defects(self, message: Message) -> list[ParseDiagnostic]:
        """Translate native email-parser defects into library diagnostics."""
        diagnostics = []
        for defect in getattr(message, "defects", ()):
            diagnostics.append(
                ParseDiagnostic(
                    code=defect.__class__.__name__,
                    message=str(defect) or defect.__class__.__name__,
                    severity=DiagnosticSeverity.ERROR
                    if self.parsing_mode == ParsingMode.STRICT
                    else DiagnosticSeverity.WARNING,
                    rfc="RFC 5322/MIME",
                )
            )
        return diagnostics

    def _populate_imf(self, result: RxMailMessage, message: Message) -> None:
        """Populate Internet Message Format fields and address structures."""
        result.Subject = str(message["Subject"] or "")
        result.Date = self._parse_date(result.Headers.get("Date", "", decoded=False))
        result.MessageID = self._parse_message_id(result.Headers.get("Message-ID", ""))
        result.InReplyTo = self._parse_message_ids(
            result.Headers.get("In-Reply-To", "")
        )
        result.References = self._parse_message_ids(
            result.Headers.get("References", "")
        )
        result.Comments = result.Headers.get_all("Comments")
        result.Keywords = result.Headers.get_all("Keywords")
        result.Received = result.Headers.get_all("Received", decoded=False)
        result.ReturnPath = result.Headers.get("Return-Path", "", decoded=False)

        address_lists = {}
        for name in _ADDRESS_HEADERS:
            raw_values = result.Headers.get_all(name)
            if not raw_values:
                continue
            combined = ", ".join(raw_values)
            wire_values = result.Headers.get_all(name, decoded=False)
            if _OBSOLETE_ROUTE.search(", ".join(wire_values)):
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="ObsoleteAddressRoute",
                        message=f"Obsolete route syntax was accepted in {name}",
                        severity=DiagnosticSeverity.WARNING,
                        rfc="RFC 5322",
                        section="4.4",
                        header=name,
                    )
                )
            try:
                address_lists[name] = AddressList(combined)
            except Exception as error:
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="InvalidAddressList",
                        message=str(error),
                        severity=DiagnosticSeverity.WARNING,
                        rfc="RFC 5322",
                        section="3.4",
                        header=name,
                    )
                )
                address_lists[name] = AddressList()
        result.From = address_lists.get("from", AddressList())
        result.Sender = address_lists.get("sender", AddressList())
        result.ReplyTo = address_lists.get("reply-to", AddressList())
        result.To = address_lists.get("to", AddressList())
        result.Cc = address_lists.get("cc", AddressList())
        result.Bcc = address_lists.get("bcc", AddressList())

        result.ResentBlocks = self._resent_blocks(result.Headers)
        result.TraceBlocks = self._trace_blocks(result.Headers)

    def _populate_mime(self, result: RxMailMessage, part: Message) -> None:
        """Populate MIME fields, message metadata, and entity diagnostics."""
        explicit_content_type = result.Headers.get("Content-Type", "", decoded=False)
        result.ContentType = ContentType()
        result.ContentType.parse(
            explicit_content_type, effective_media_type=part.get_content_type()
        )

        disposition = result.Headers.get("Content-Disposition", "", decoded=False)
        if disposition:
            result.ContentDisposition = ContentDisposition()
            result.ContentDisposition.parse(disposition)

        transfer_encoding = (part.get("Content-Transfer-Encoding") or "7bit").strip()
        result.ContentTransferEncoding = TransferEncodingValue.parse(transfer_encoding)
        result.MimeVersion = result.Headers.get("MIME-Version", "", decoded=False)
        result.ContentDescription = str(part.get("Content-Description") or "")
        result.ContentID = self._parse_message_id(result.Headers.get("Content-ID", ""))

        media_type = result.ContentType.MediaType.lower()
        self._populate_message_metadata(result, media_type)
        self._validate_mime_entity(result, part, media_type)

    def _populate_message_metadata(
        self, result: RxMailMessage, media_type: str
    ) -> None:
        """Project parameters for message/partial and message/external-body."""
        parameters = result.ContentType.Parameters
        if media_type == "message/partial":
            number = parameters.get("number", "")
            total = parameters.get("total", "")
            result.MessagePartial = MessagePartialInfo(
                id=parameters.get("id", ""),
                number=int(number) if number.isdigit() else None,
                total=int(total) if total.isdigit() else None,
            )
        elif media_type == "message/external-body":
            result.ExternalBodyAccess = ExternalBodyAccessInfo(
                access_type=parameters.get("access-type", ""),
                parameters=dict(parameters),
            )

    def _validate_mime_entity(
        self, result: RxMailMessage, part: Message, media_type: str
    ) -> None:
        """Validate content-type parameters and composite transfer encodings."""
        explicit = result.ContentType
        if media_type.startswith("multipart/"):
            boundary = part.get_boundary()
            if not boundary:
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="MissingMultipartBoundary",
                        message="A multipart Content-Type requires a boundary parameter",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 2046",
                        section="5.1.1",
                        header="Content-Type",
                    )
                )
            elif len(boundary) > 70:
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="MultipartBoundaryTooLong",
                        message="A MIME boundary must not exceed 70 characters",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 2046",
                        section="5.1.1",
                        header="Content-Type",
                    )
                )
        if media_type == "message/partial":
            metadata = result.MessagePartial
            if (
                metadata is None
                or not metadata.id
                or metadata.number is None
                or metadata.number < 1
            ):
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="InvalidMessagePartialParameters",
                        message="message/partial requires id and a positive number parameter",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 2046",
                        section="5.2.2",
                        header="Content-Type",
                    )
                )
            elif metadata.total is not None and metadata.total < metadata.number:
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="InvalidMessagePartialTotal",
                        message="message/partial total cannot be smaller than number",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 2046",
                        section="5.2.2",
                        header="Content-Type",
                    )
                )
        if media_type == "message/external-body" and (
            result.ExternalBodyAccess is None
            or not result.ExternalBodyAccess.access_type
        ):
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="MissingExternalBodyAccessType",
                    message="message/external-body requires an access-type parameter",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 2046",
                    section="5.2.3",
                    header="Content-Type",
                )
            )
        restricted_composite = media_type.startswith("multipart/") or (
            media_type.startswith("message/") and media_type != "message/global"
        )
        if restricted_composite and result.ContentTransferEncoding.kind in (
            TransferEncoding.BASE64,
            TransferEncoding.QUOTED_PRINTABLE,
        ):
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="InvalidCompositeTransferEncoding",
                    message="Composite multipart/message entities cannot use base64 or quoted-printable",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 2045",
                    section="6.4",
                    header="Content-Transfer-Encoding",
                )
            )
        if (
            explicit
            and explicit.MediaType.startswith("text/")
            and "charset" not in explicit.Parameters
        ):
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="ImplicitUSASCIICharset",
                    message="Text entity has no charset parameter; US-ASCII is the MIME default",
                    severity=DiagnosticSeverity.INFO,
                    rfc="RFC 2046",
                    section="4.1.2",
                    header="Content-Type",
                )
            )

    def _populate_leaf_body(
        self, result: RxMailMessage, part: Message, top_level: bool = False
    ) -> None:
        """Transfer-decode a leaf and decode text using its declared charset."""
        native_decoded = part.get_payload(decode=True)
        if isinstance(native_decoded, bytes):
            decoded = native_decoded
        elif isinstance(native_decoded, str):
            decoded = native_decoded.encode("utf-8", "surrogateescape")
        else:
            payload = part.get_payload()
            decoded = (
                payload.encode("utf-8", "surrogateescape")
                if isinstance(payload, str)
                else b""
            )
        result.DecodedBody = decoded
        if len(decoded) > self.limits.max_decoded_part_bytes:
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="DecodedPartLimitExceeded",
                    message=f"Decoded MIME part exceeds {self.limits.max_decoded_part_bytes} bytes",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 2045",
                )
            )
        media_type = part.get_content_type().lower()
        if media_type.startswith("text/"):
            charset = part.get_content_charset() or "us-ascii"
            try:
                text = decoded.decode(charset)
            except (LookupError, UnicodeDecodeError):
                text = decoded.decode("utf-8", "replace")
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="InvalidCharsetData",
                        message=f"Body could not be decoded using {charset}",
                        severity=DiagnosticSeverity.WARNING,
                        rfc="RFC 2045",
                    )
                )
            result._DecodedText = text.rstrip("\r\n") if top_level else text

    def _validate_required(self, result: RxMailMessage) -> None:
        """Validate root IMF requirements, singleton fields, and MIME version."""
        for name in ("Date", "From"):
            if not result.Headers.get_all(name):
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code=f"MissingRequired{name}",
                        message=f"Required {name} header is missing",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 5322",
                        section="3.6",
                        header=name,
                    )
                )
        for name in _IMF_SINGLETON_HEADERS:
            occurrences = result.Headers.occurrences(name)
            if len(occurrences) > 1:
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="DuplicateSingletonHeader",
                        message=f"{name} occurs {len(occurrences)} times but may occur at most once",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 5322/MIME",
                        section="3.6/3",
                        header=name,
                    )
                )
        if result.Headers.get_all("Date") and (
            result.Date is None or not result.Date.valid
        ):
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="InvalidDate",
                    message="Date is not a valid RFC 5322 date-time",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 5322",
                    section="3.3",
                    header="Date",
                )
            )
        if result.Headers.get_all("Message-ID") and (
            result.MessageID is None or not result.MessageID.valid
        ):
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="InvalidMessageID",
                    message="Message-ID is not a valid msg-id",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 5322/RFC 6532",
                    section="3.6.4/3.3",
                    header="Message-ID",
                )
            )
        self._validate_resent_blocks(result)
        has_mime_fields = any(
            result.Headers.get_all(name) for name in _MIME_SINGLETON_HEADERS
        )
        if has_mime_fields and not result.MimeVersion:
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="MissingMIMEVersion",
                    message="MIME content fields are present without MIME-Version",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 2045",
                    section="4",
                    header="MIME-Version",
                )
            )
        mime_version = result.MimeVersion
        previous = None
        while mime_version != previous:
            previous = mime_version
            mime_version = re.sub(r"\([^()]*\)", "", mime_version)
        if result.MimeVersion and not re.fullmatch(
            r"\s*\d+\s*\.\s*\d+\s*", mime_version
        ):
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="InvalidMIMEVersion",
                    message="MIME-Version must use major.minor numeric syntax",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 2045",
                    section="4",
                    header="MIME-Version",
                )
            )
        elif result.MimeVersion and re.sub(r"\s+", "", mime_version) != "1.0":
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="UnsupportedMIMEVersion",
                    message=f"MIME version {mime_version.strip()} is syntactically valid but not defined by this bundle",
                    severity=DiagnosticSeverity.WARNING,
                    rfc="RFC 2045",
                    section="4",
                    header="MIME-Version",
                )
            )
        if len(result.From.Mailboxes) > 1 and not result.Headers.get_all("Sender"):
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="MissingRequiredSender",
                    message="Sender is required when From contains multiple mailboxes",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 5322/RFC 6854",
                    section="3.6.2",
                    header="Sender",
                )
            )
        if len(result.Sender.Mailboxes) > 1:
            result.Diagnostics.append(
                ParseDiagnostic(
                    code="InvalidSenderGroup",
                    message="A Sender group must not contain more than one mailbox",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 6854",
                    section="2.1",
                    header="Sender",
                )
            )
        for name in ("From", "Sender"):
            address_list = result.From if name == "From" else result.Sender
            if address_list and any(
                isinstance(item, AddressGroup) for item in address_list.Items
            ):
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="LimitedUseOriginatorGroup",
                        message=f"Group syntax in {name} is valid but RFC 6854 limits its use",
                        severity=DiagnosticSeverity.WARNING,
                        rfc="RFC 6854",
                        section="3",
                        header=name,
                    )
                )

    @staticmethod
    def _validate_entity_headers(result: RxMailMessage) -> None:
        """Reject duplicate MIME singleton fields within one entity."""
        for name in _MIME_SINGLETON_HEADERS:
            occurrences = result.Headers.occurrences(name)
            if len(occurrences) > 1:
                result.Diagnostics.append(
                    ParseDiagnostic(
                        code="DuplicateMIMEHeader",
                        message=f"{name} occurs {len(occurrences)} times in one MIME entity",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 2045",
                        section="3",
                        header=name,
                    )
                )

    @staticmethod
    def _validate_resent_blocks(result: RxMailMessage) -> None:
        """Validate required fields and sender rules in every Resent block."""
        for index, block in enumerate(result.ResentBlocks, start=1):
            for name in ("Resent-Date", "Resent-From"):
                if not block.fields.get_all(name):
                    result.Diagnostics.append(
                        ParseDiagnostic(
                            code="IncompleteResentBlock",
                            message=f"Resent block {index} is missing {name}",
                            severity=DiagnosticSeverity.ERROR,
                            rfc="RFC 5322",
                            section="3.6.6",
                            header=name,
                        )
                    )
            from_values = block.fields.get_all("Resent-From")
            if from_values:
                addresses = AddressList(", ".join(from_values))
                if len(addresses.Mailboxes) > 1 and not block.fields.get_all(
                    "Resent-Sender"
                ):
                    result.Diagnostics.append(
                        ParseDiagnostic(
                            code="MissingRequiredResentSender",
                            message=f"Resent block {index} needs Resent-Sender for multiple mailboxes",
                            severity=DiagnosticSeverity.ERROR,
                            rfc="RFC 5322",
                            section="3.6.6",
                            header="Resent-Sender",
                        )
                    )
            sender_values = block.fields.get_all("Resent-Sender")
            if sender_values:
                sender = AddressList(", ".join(sender_values))
                if len(sender.Mailboxes) > 1:
                    result.Diagnostics.append(
                        ParseDiagnostic(
                            code="InvalidResentSenderGroup",
                            message=f"Resent block {index} has more than one Resent-Sender mailbox",
                            severity=DiagnosticSeverity.ERROR,
                            rfc="RFC 6854",
                            section="2.2",
                            header="Resent-Sender",
                        )
                    )

    def _source_diagnostics(
        self, source: bytes, headers: HeaderCollection
    ) -> list[ParseDiagnostic]:
        """Inspect root bytes for limits, UTF-8, line endings, and line length."""
        diagnostics = []
        if len(source) > self.limits.max_message_bytes:
            diagnostics.append(
                ParseDiagnostic(
                    code="MessageSizeLimitExceeded",
                    message=f"Message exceeds {self.limits.max_message_bytes} bytes",
                    severity=DiagnosticSeverity.ERROR,
                )
            )
        separator = re.search(rb"\r\n\r\n|\n\n|\r\r", source)
        header_bytes = source[: separator.start()] if separator else source
        if len(header_bytes) > self.limits.max_header_bytes:
            diagnostics.append(
                ParseDiagnostic(
                    code="HeaderSizeLimitExceeded",
                    message=f"Header section exceeds {self.limits.max_header_bytes} bytes",
                    severity=DiagnosticSeverity.ERROR,
                )
            )
        try:
            header_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            diagnostics.append(
                ParseDiagnostic(
                    code="InvalidUTF8Header",
                    message=f"Header section contains invalid UTF-8 at byte {error.start}",
                    severity=DiagnosticSeverity.ERROR,
                    rfc="RFC 6532",
                    section="3.2",
                )
            )
        if len(headers) > self.limits.max_header_count:
            diagnostics.append(
                ParseDiagnostic(
                    code="HeaderCountLimitExceeded",
                    message=f"Header count exceeds {self.limits.max_header_count}",
                    severity=DiagnosticSeverity.ERROR,
                )
            )
        if re.search(rb"(?<!\r)\n|\r(?!\n)", source):
            diagnostics.append(
                ParseDiagnostic(
                    code="ObsoleteLineEnding",
                    message="Bare CR or LF line endings were accepted in receiver mode",
                    severity=DiagnosticSeverity.WARNING,
                    rfc="RFC 5322",
                    section="4.1",
                )
            )
        for line_number, line in enumerate(re.split(rb"\r\n|\n|\r", source), start=1):
            if len(line) > 998:
                diagnostics.append(
                    ParseDiagnostic(
                        code="LineTooLong",
                        message=f"Line contains {len(line)} octets; maximum is 998",
                        severity=DiagnosticSeverity.ERROR,
                        rfc="RFC 5322/RFC 6532",
                        section="2.1.1/3.4",
                        line=line_number,
                    )
                )
            elif len(line) > 78:
                diagnostics.append(
                    ParseDiagnostic(
                        code="LongLine",
                        message=f"Line contains {len(line)} octets; 78 is recommended",
                        severity=DiagnosticSeverity.INFO,
                        rfc="RFC 5322",
                        section="2.1.1",
                        line=line_number,
                    )
                )
        return diagnostics

    @staticmethod
    def _parse_date(raw: str) -> ParsedDateTime | None:
        """Parse a date while retaining invalid and obsolete source syntax."""
        if not raw:
            return None
        try:
            obsolete = bool(
                re.search(
                    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2}\b",
                    raw,
                    re.I,
                )
                or re.search(
                    r"\b(?:UT|GMT|EST|EDT|CST|CDT|MST|MDT|PST|PDT|[A-IK-Z])\b",
                    raw,
                    re.I,
                )
            )
            return ParsedDateTime(raw, parsedate_to_datetime(raw), True, obsolete)
        except (TypeError, ValueError, OverflowError):
            return ParsedDateTime(raw, None, False)

    @staticmethod
    def _parse_message_id(raw: str) -> ParsedMessageID | None:
        """Parse one msg-id while retaining decomposed invalid input."""
        if not raw:
            return None
        match = _MSG_ID.match(raw)
        if not match:
            value = raw.strip().removeprefix("<").removesuffix(">")
            left, separator, right = value.partition("@")
            return ParsedMessageID(raw, value, left, right if separator else "", False)
        return ParsedMessageID(
            raw,
            f"{match.group(1)}@{match.group(2)}",
            match.group(1),
            match.group(2),
            True,
        )

    @classmethod
    def _parse_message_ids(cls, raw: str) -> list[ParsedMessageID]:
        """Extract and parse every bracketed msg-id from a field value."""
        return [
            item
            for value in _MSG_IDS.findall(raw or "")
            if (item := cls._parse_message_id(value))
        ]

    @staticmethod
    def _resent_blocks(headers: HeaderCollection) -> list[ResentBlock]:
        """Group contiguous Resent fields into ordered blocks."""
        blocks = []
        current = HeaderCollection()
        for field in headers:
            if field.name.casefold() in _RESENT_HEADERS:
                if field.name.casefold() == "resent-date" and len(current):
                    blocks.append(ResentBlock(current))
                    current = HeaderCollection()
                current.append(field)
            elif len(current):
                blocks.append(ResentBlock(current))
                current = HeaderCollection()
        if len(current):
            blocks.append(ResentBlock(current))
        return blocks

    @staticmethod
    def _trace_blocks(headers: HeaderCollection) -> list[TraceBlock]:
        """Group Return-Path and Received occurrences into trace blocks."""
        blocks = []
        current = None
        for field in headers:
            key = field.name.casefold()
            if key == "return-path":
                if current and current.received:
                    blocks.append(current)
                current = TraceBlock(return_path=field.unfolded_value)
            elif key == "received":
                if current is None:
                    current = TraceBlock()
                current.received.append(field.unfolded_value)
            elif current and current.received:
                blocks.append(current)
                current = None
        if current and (current.return_path is not None or current.received):
            blocks.append(current)
        return blocks
