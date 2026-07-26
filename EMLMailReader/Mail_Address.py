"""Structured mailbox and address-group models for Internet message fields."""

from .Text_Encoding import TextEncoding
from .Standards import AddressGroup
from email.parser import HeaderParser
from email.policy import default
from email.headerregistry import Address


class MailAddress:
    """Represent one mailbox from an RFC 5322 or RFC 6532 address field.

    Attributes:
        DisplayName: Decoded human-readable phrase preceding the address.
        Email: Complete address specification.
        LocalPart: Portion of the address before ``@``.
        Domain: Portion of the address after ``@``.
        RawValue: Original mailbox value when available.
        IsInternationalized: Whether the source contains non-ASCII characters.
    """

    def __init__(self):
        """Initialize an empty mailbox."""
        self.DisplayName = str()
        """The human-readable name associated with the email address (optional)."""
        self.Email = str()
        """The actual email address (user@domain.com format)."""
        self.LocalPart = str()
        self.Domain = str()
        self.RawValue = str()
        self.IsInternationalized = False

    def parse(self, MailAddressString: str):
        """Parse the first mailbox from a source address value.

        The instance is reset before parsing. If the standard header parser
        rejects the value, a conservative fallback retains as much display-name
        and address text as possible.

        Args:
            MailAddressString: Mailbox value such as
                ``"Jane Doe <jane@example.com>"``.
        """
        value = (MailAddressString or "").strip()
        self.DisplayName = ""
        self.Email = ""
        self.LocalPart = ""
        self.Domain = ""
        self.IsInternationalized = False
        self.RawValue = value
        try:
            header = HeaderParser(policy=default).parsestr(f"To: {value}\n")["To"]
            addresses = tuple(getattr(header, "addresses", ()))
            if addresses:
                parsed = addresses[0]
                self.DisplayName = parsed.display_name or ""
                self.LocalPart = parsed.username or ""
                self.Domain = parsed.domain or ""
                self.Email = parsed.addr_spec or ""
            else:
                self.Email = value
        except Exception:
            if "<" not in value:
                self.Email = value
            else:
                index = value.find("<")
                name_value = value[0:index].strip().strip('"')
                self.DisplayName = TextEncoding.decode_header(name_value)
                index_one = value.find(">", index)
                self.Email = value[index + 1:index_one if index_one >= 0 else None].strip()
        if not self.LocalPart and "@" in self.Email:
            self.LocalPart, self.Domain = self.Email.rsplit("@", 1)
        self.IsInternationalized = any(ord(character) > 127 for character in value)

    @classmethod
    def from_parts(cls, display_name: str, username: str, domain: str, raw_value: str = ""):
        """Build a mailbox from components produced by the header registry.

        Args:
            display_name: Decoded display phrase.
            username: Local part of the address.
            domain: Domain part of the address.
            raw_value: Optional source representation to retain.

        Returns:
            A populated :class:`MailAddress`.
        """
        address = cls()
        address.DisplayName = display_name or ""
        address.LocalPart = username or ""
        address.Domain = domain or ""
        address.Email = f"{address.LocalPart}@{address.Domain}" if address.Domain else address.LocalPart
        address.RawValue = raw_value or str(address)
        address.IsInternationalized = any(ord(character) > 127 for character in address.RawValue)
        return address

    def to_dict(self) -> dict:
        """Return a JSON-compatible mailbox representation."""
        return {
            "display_name": self.DisplayName,
            "email": self.Email,
            "local_part": self.LocalPart,
            "domain": self.Domain,
            "raw_value": self.RawValue,
            "internationalized": self.IsInternationalized,
        }

    def to_header_value(self) -> str:
        """Return a normalized mailbox value suitable for an address header."""
        return str(self)

    def __str__(self) -> str:
        """Return the mailbox as a normalized address-header value."""
        try:
            return str(Address(
                display_name=self.DisplayName,
                username=self.LocalPart or self.Email,
                domain=self.Domain,
            ))
        except (TypeError, ValueError):
            if self.DisplayName:
                return f"{self.DisplayName} <{self.Email}>"
            return self.Email


class AddressList:
    """Represent a mailbox list while retaining named and empty groups.

    Attributes:
        RawValue: Original complete address-list value.
        Items: Ordered top-level :class:`MailAddress` and
            :class:`AddressGroup` values.
    """

    def __init__(self, raw_value: str = ""):
        """Initialize an address list and optionally parse a source value."""
        self.RawValue = raw_value
        self.Items = []
        if raw_value:
            self.parse(raw_value)

    def parse(self, value: str):
        """Parse an RFC 5322/6854 address list in place.

        Args:
            value: Complete address-list value without the header name.

        Returns:
            This instance, allowing fluent construction.
        """
        self.RawValue = value or ""
        self.Items = []
        header = HeaderParser(policy=default).parsestr(f"To: {self.RawValue}\n")["To"]
        for group in tuple(getattr(header, "groups", ())):
            mailboxes = tuple(
                MailAddress.from_parts(item.display_name, item.username, item.domain)
                for item in tuple(getattr(group, "addresses", ()))
            )
            if getattr(group, "display_name", None) is not None:
                self.Items.append(AddressGroup(group.display_name or "", mailboxes, self.RawValue))
            else:
                self.Items.extend(mailboxes)
        return self

    @property
    def Mailboxes(self) -> tuple[MailAddress, ...]:
        """Return all direct and grouped mailboxes as an immutable flat tuple."""
        mailboxes = []
        for item in self.Items:
            if isinstance(item, AddressGroup):
                mailboxes.extend(item.addresses)
            else:
                mailboxes.append(item)
        return tuple(mailboxes)

    def __iter__(self):
        """Iterate over top-level mailboxes and address groups in source order."""
        return iter(self.Items)

    def __len__(self):
        """Return the number of top-level mailbox or group items."""
        return len(self.Items)

    def __bool__(self):
        """Return whether parsed items or a source value are present."""
        return bool(self.Items) or bool(self.RawValue)

    def to_header_value(self) -> str:
        """Return a normalized address-list value while preserving groups."""
        values = []
        for item in self.Items:
            if isinstance(item, AddressGroup):
                members = ", ".join(address.to_header_value() for address in item.addresses)
                values.append(f"{item.display_name}: {members};")
            else:
                values.append(item.to_header_value())
        return ", ".join(values)

    def to_dict(self) -> list[dict]:
        """Return ordered JSON-compatible mailbox and group records."""
        result = []
        for item in self.Items:
            if isinstance(item, AddressGroup):
                result.append({"type": "group", **item.to_dict()})
            else:
                result.append({"type": "mailbox", **item.to_dict()})
        return result

    def __str__(self) -> str:
        """Return the normalized address-list header value."""
        return self.to_header_value()
