"""Standards-aware, lossless data structures used by the EML parser.

The original public model is intentionally kept intact.  These types provide
the richer RFC 5322/MIME view without forcing existing callers to change.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable, Iterator, Sequence

from .Enumerations import TransferEncoding


class ParsingMode(str, Enum):
    """Controls how syntax defects affect parsing."""

    MODERN = "modern"
    LENIENT = "lenient"
    STRICT = "strict"


class SyntaxStatus(str, Enum):
    CURRENT = "current"
    OBSOLETE = "obsolete"
    NONCONFORMANT = "nonconformant"


class DiagnosticSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class StandardsComplianceError(ValueError):
    """Raised by strict mode while retaining the complete diagnostic report."""

    def __init__(self, diagnostics):
        self.diagnostics = tuple(diagnostics)
        codes = ", ".join(item.code for item in self.diagnostics if item.severity == DiagnosticSeverity.ERROR)
        super().__init__(f"Message is not conformant: {codes or 'unknown error'}")


@dataclass(frozen=True)
class ParserLimits:
    """Resource guards for hostile or accidentally enormous messages."""

    max_message_bytes: int = 100 * 1024 * 1024
    max_header_bytes: int = 1024 * 1024
    max_header_count: int = 10_000
    max_mime_depth: int = 100
    max_parts: int = 10_000
    max_decoded_part_bytes: int = 100 * 1024 * 1024


@dataclass(frozen=True)
class ParseDiagnostic:
    code: str
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.WARNING
    rfc: str | None = None
    section: str | None = None
    header: str | None = None
    line: int | None = None
    column: int | None = None

    def to_dict(self) -> dict:
        result = asdict(self)
        result["severity"] = self.severity.value
        return result


@dataclass(frozen=True)
class HeaderField:
    """One header occurrence, preserving both wire and interpreted forms."""

    name: str
    raw_name: str
    raw_value: str
    unfolded_value: str
    decoded_value: str
    index: int
    line: int | None = None
    syntax_status: SyntaxStatus = SyntaxStatus.CURRENT

    def to_dict(self) -> dict:
        result = asdict(self)
        result["syntax_status"] = self.syntax_status.value
        return result


class HeaderCollection(Sequence[HeaderField]):
    """Ordered, duplicate-preserving collection with case-insensitive lookup."""

    def __init__(self, fields: Iterable[HeaderField] | None = None):
        self._fields = list(fields or [])

    def __len__(self) -> int:
        return len(self._fields)

    def __getitem__(self, index):
        return self._fields[index]

    def __iter__(self) -> Iterator[HeaderField]:
        return iter(self._fields)

    def append(self, value: HeaderField) -> None:
        self._fields.append(value)

    def get(self, name: str, default=None, *, decoded: bool = True):
        values = self.get_all(name, decoded=decoded)
        return values[-1] if values else default

    def get_all(self, name: str, *, decoded: bool = True) -> list[str]:
        key = name.casefold()
        return [
            field.decoded_value if decoded else field.unfolded_value
            for field in self._fields
            if field.name.casefold() == key
        ]

    def occurrences(self, name: str) -> list[HeaderField]:
        key = name.casefold()
        return [field for field in self._fields if field.name.casefold() == key]

    def to_list(self) -> list[dict]:
        return [field.to_dict() for field in self._fields]


@dataclass(frozen=True)
class TransferEncodingValue:
    """One lossless Content-Transfer-Encoding value."""

    raw_value: str
    kind: TransferEncoding
    is_extension: bool = False

    @classmethod
    def parse(cls, value: str | None):
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

    def to_dict(self) -> dict:
        return {
            "raw_value": self.raw_value,
            "kind": self.kind.value,
            "is_extension": self.is_extension,
        }


@dataclass(frozen=True)
class AddressGroup:
    display_name: str
    addresses: tuple
    raw_value: str = ""

    def to_dict(self) -> dict:
        return {
            "display_name": self.display_name,
            "addresses": [address.to_dict() for address in self.addresses],
            "raw_value": self.raw_value,
        }


@dataclass(frozen=True)
class ParsedMessageID:
    raw_value: str
    value: str
    left: str
    right: str
    valid: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ParsedDateTime:
    raw_value: str
    value: datetime | None
    valid: bool
    obsolete: bool = False

    def to_dict(self) -> dict:
        return {
            "raw_value": self.raw_value,
            "value": self.value.isoformat() if self.value else None,
            "valid": self.valid,
            "obsolete": self.obsolete,
        }


@dataclass(frozen=True)
class MessagePartialInfo:
    """RFC 2046 message/partial reassembly metadata."""

    id: str
    number: int | None
    total: int | None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ExternalBodyAccessInfo:
    """RFC 2046 message/external-body access metadata."""

    access_type: str
    parameters: dict

    def to_dict(self) -> dict:
        return {"access_type": self.access_type, "parameters": dict(self.parameters)}


@dataclass
class ResentBlock:
    fields: HeaderCollection = field(default_factory=HeaderCollection)

    def to_dict(self) -> list[dict]:
        return self.fields.to_list()


@dataclass
class TraceBlock:
    return_path: str | None = None
    received: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"return_path": self.return_path, "received": list(self.received)}
