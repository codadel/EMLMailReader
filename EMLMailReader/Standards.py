"""Standards, diagnostics, limits, and lossless structured parser values."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, TypeVar, overload

from .Enumerations import TransferEncoding

if TYPE_CHECKING:
    from .Mail_Address import MailAddress

type JsonValue = (
    bool | int | float | str | Sequence[JsonValue] | Mapping[str, JsonValue] | None
)
type JsonObject = dict[str, JsonValue]

_DefaultT = TypeVar("_DefaultT")


class ParsingMode(str, Enum):
    """Control how parser diagnostics affect the result.

    ``MODERN`` and ``LENIENT`` return recoverable messages with diagnostics.
    ``STRICT`` raises when any error-level diagnostic is collected.
    """

    MODERN = "modern"
    LENIENT = "lenient"
    STRICT = "strict"


class SyntaxStatus(str, Enum):
    """Classify header syntax as current, accepted obsolete, or invalid."""

    CURRENT = "current"
    OBSOLETE = "obsolete"
    NONCONFORMANT = "nonconformant"


class DiagnosticSeverity(str, Enum):
    """Classify a finding as informational, recoverable, or error-level."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class StandardsComplianceError(ValueError):
    """Report strict-mode failure with the complete diagnostic collection.

    Attributes:
        diagnostics: Immutable root and nested diagnostics collected before the
            exception was raised.
    """

    def __init__(self, diagnostics: Iterable[ParseDiagnostic]) -> None:
        """Create an exception from an iterable of parser diagnostics."""
        self.diagnostics: tuple[ParseDiagnostic, ...] = tuple(diagnostics)
        codes = ", ".join(
            item.code
            for item in self.diagnostics
            if item.severity == DiagnosticSeverity.ERROR
        )
        super().__init__(f"Message is not conformant: {codes or 'unknown error'}")


@dataclass(frozen=True)
class ParserLimits:
    """Set resource guards for hostile or accidentally enormous messages.

    Attributes:
        max_message_bytes: Maximum complete source size.
        max_header_bytes: Maximum root header-section size.
        max_header_count: Maximum root header occurrence count.
        max_mime_depth: Maximum recursive MIME depth.
        max_parts: Maximum MIME entity count, including the root.
        max_decoded_part_bytes: Maximum transfer-decoded size per leaf.
    """

    max_message_bytes: int = 100 * 1024 * 1024
    max_header_bytes: int = 1024 * 1024
    max_header_count: int = 10_000
    max_mime_depth: int = 100
    max_parts: int = 10_000
    max_decoded_part_bytes: int = 100 * 1024 * 1024


@dataclass(frozen=True)
class ParseDiagnostic:
    """Describe one standards, syntax, decoding, or resource-limit finding.

    Attributes:
        code: Stable machine-readable diagnostic identifier.
        message: Human-readable explanation.
        severity: Informational, warning, or error impact.
        rfc: Relevant RFC label when known.
        section: Relevant standards section when known.
        header: Associated header field name when applicable.
        line: One-based source line when known.
        column: One-based source column when known.
    """

    code: str
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.WARNING
    rfc: str | None = None
    section: str | None = None
    header: str | None = None
    line: int | None = None
    column: int | None = None

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible diagnostic record."""
        result = asdict(self)
        result["severity"] = self.severity.value
        return result


@dataclass(frozen=True)
class HeaderField:
    """Represent one header occurrence without losing source information.

    Attributes:
        name: Lookup name for the field.
        raw_name: Field name as it appeared in the source.
        raw_value: Folded source value.
        unfolded_value: Source value with legal folding removed.
        decoded_value: Interpreted Unicode value.
        index: Zero-based position in the header block.
        line: One-based source line when available.
        syntax_status: Current, obsolete, or nonconformant syntax classification.
    """

    name: str
    raw_name: str
    raw_value: str
    unfolded_value: str
    decoded_value: str
    index: int
    line: int | None = None
    syntax_status: SyntaxStatus = SyntaxStatus.CURRENT

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible header occurrence."""
        result = asdict(self)
        result["syntax_status"] = self.syntax_status.value
        return result


class HeaderCollection(Sequence[HeaderField]):
    """Store ordered duplicate headers with case-insensitive lookup."""

    def __init__(self, fields: Iterable[HeaderField] | None = None) -> None:
        """Initialize the collection from optional header occurrences."""
        self._fields = list(fields or [])

    def __len__(self) -> int:
        """Return the number of header occurrences."""
        return len(self._fields)

    @overload
    def __getitem__(self, index: int) -> HeaderField: ...

    @overload
    def __getitem__(self, index: slice) -> list[HeaderField]: ...

    def __getitem__(self, index: int | slice) -> HeaderField | list[HeaderField]:
        """Return an occurrence or slice using sequence indexing."""
        return self._fields[index]

    def __iter__(self) -> Iterator[HeaderField]:
        """Iterate over header occurrences in source order."""
        return iter(self._fields)

    def append(self, value: HeaderField) -> None:
        """Append a header occurrence without deduplicating its name."""
        self._fields.append(value)

    @overload
    def get(
        self, name: str, default: None = None, *, decoded: bool = True
    ) -> str | None: ...

    @overload
    def get(
        self, name: str, default: _DefaultT, *, decoded: bool = True
    ) -> str | _DefaultT: ...

    def get(
        self, name: str, default: _DefaultT | None = None, *, decoded: bool = True
    ) -> str | _DefaultT | None:
        """Return the last matching value or a default.

        Args:
            name: Case-insensitive field name.
            default: Value returned when no occurrence exists.
            decoded: Select decoded text instead of unfolded source text.
        """
        values = self.get_all(name, decoded=decoded)
        return values[-1] if values else default

    def get_all(self, name: str, *, decoded: bool = True) -> list[str]:
        """Return all matching values in source order."""
        key = name.casefold()
        return [
            field.decoded_value if decoded else field.unfolded_value
            for field in self._fields
            if field.name.casefold() == key
        ]

    def occurrences(self, name: str) -> list[HeaderField]:
        """Return all matching :class:`HeaderField` objects in source order."""
        key = name.casefold()
        return [field for field in self._fields if field.name.casefold() == key]

    def to_list(self) -> list[JsonObject]:
        """Serialize every occurrence in source order."""
        return [field.to_dict() for field in self._fields]


@dataclass(frozen=True)
class TransferEncodingValue:
    """Represent a known or extension Content-Transfer-Encoding token.

    Attributes:
        raw_value: Normalized lowercase token from the field.
        kind: Matching known :class:`TransferEncoding` or ``UNKNOWN``.
        is_extension: Whether the token is not one of the standard encodings.
    """

    raw_value: str
    kind: TransferEncoding
    is_extension: bool = False

    @classmethod
    def parse(cls, value: str | None) -> TransferEncodingValue:
        """Classify a transfer-encoding token without discarding extensions."""
        token = (value or "7bit").strip().lower()
        known = {
            "7bit": TransferEncoding.SEVEN_BIT,
            "8bit": TransferEncoding.EIGHT_BIT,
            "binary": TransferEncoding.BINARY,
            "base64": TransferEncoding.BASE64,
            "quoted-printable": TransferEncoding.QUOTED_PRINTABLE,
        }
        kind = known.get(token, TransferEncoding.UNKNOWN)
        return cls(token, kind, kind == TransferEncoding.UNKNOWN)

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible transfer-encoding record."""
        return {
            "raw_value": self.raw_value,
            "kind": self.kind.value,
            "is_extension": self.is_extension,
        }


@dataclass(frozen=True)
class AddressGroup:
    """Represent a named or empty address group.

    Attributes:
        display_name: Group phrase preceding the colon.
        addresses: Ordered member mailboxes.
        raw_value: Source address-list value retained for diagnostics or display.
    """

    display_name: str
    addresses: tuple[MailAddress, ...]
    raw_value: str = ""

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible group and its member mailboxes."""
        return {
            "display_name": self.display_name,
            "addresses": [address.to_dict() for address in self.addresses],
            "raw_value": self.raw_value,
        }


@dataclass(frozen=True)
class ParsedMessageID:
    """Retain raw and decomposed forms of an Internet message identifier.

    Attributes:
        raw_value: Source value, normally including angle brackets.
        value: Identifier without surrounding angle brackets.
        left: Identifier portion before ``@``.
        right: Identifier portion after ``@``.
        valid: Whether the source matched the supported msg-id syntax.
    """

    raw_value: str
    value: str
    left: str
    right: str
    valid: bool = True

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible message-identifier record."""
        return asdict(self)


@dataclass(frozen=True)
class ParsedDateTime:
    """Retain a source date together with its parsed Python value.

    Attributes:
        raw_value: Original date-time field value.
        value: Parsed timezone-aware or naive datetime, or ``None``.
        valid: Whether parsing succeeded.
        obsolete: Whether accepted obsolete date syntax was detected.
    """

    raw_value: str
    value: datetime | None
    valid: bool
    obsolete: bool = False

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible date record using ISO 8601 text."""
        return {
            "raw_value": self.raw_value,
            "value": self.value.isoformat() if self.value else None,
            "valid": self.valid,
            "obsolete": self.obsolete,
        }


@dataclass(frozen=True)
class MessagePartialInfo:
    """Represent RFC 2046 ``message/partial`` reassembly metadata.

    Attributes:
        id: Identifier shared by all fragments.
        number: One-based fragment number.
        total: Declared total fragment count when present.
    """

    id: str
    number: int | None
    total: int | None

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible fragment metadata record."""
        return asdict(self)


@dataclass(frozen=True)
class ExternalBodyAccessInfo:
    """Represent RFC 2046 ``message/external-body`` access metadata.

    Attributes:
        access_type: Mechanism used to retrieve the external body.
        parameters: Complete decoded Content-Type parameter mapping.
    """

    access_type: str
    parameters: dict[str, str]

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible external-body metadata record."""
        return {"access_type": self.access_type, "parameters": dict(self.parameters)}


@dataclass
class ResentBlock:
    """Group one contiguous set of RFC 5322 Resent fields.

    Attributes:
        fields: Ordered header occurrences belonging to the block.
    """

    fields: HeaderCollection = field(default_factory=HeaderCollection)

    def to_dict(self) -> list[JsonObject]:
        """Serialize the block as its ordered header-field records."""
        return self.fields.to_list()


@dataclass
class TraceBlock:
    """Group one Return-Path with its following Received trace fields.

    Attributes:
        return_path: Unfolded Return-Path value when present.
        received: Unfolded Received values in source order.
    """

    return_path: str | None = None
    received: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible trace block."""
        return {"return_path": self.return_path, "received": list(self.received)}
