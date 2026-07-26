from .Text_Encoding import TextEncoding
from .Standards import AddressGroup
from email.parser import HeaderParser
from email.policy import default
from email.headerregistry import Address


class MailAddress:
    """
    A class to represent an email address with optional display name.

    This class parses and stores email addresses in the format used by email headers,
    supporting both simple addresses (user@domain.com) and addresses with display names
    ("John Doe" <user@domain.com>).
    """
    def __init__(self):
        self.DisplayName = str()
        """The human-readable name associated with the email address (optional)."""
        self.Email = str()
        """The actual email address (user@domain.com format)."""
        self.LocalPart = str()
        self.Domain = str()
        self.RawValue = str()
        self.IsInternationalized = False

    def parse(self, MailAddressString: str):
        """
        Parses an email address string and extracts the display name and email components.

        This method handles both simple email addresses and those with display names,
        automatically decoding any encoded header content in the display name portion.

        :param MailAddressString: Email address string to parse (e.g., "John Doe <john@example.com>").
        :returns: None - modifies the object's properties in place.
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
        address = cls()
        address.DisplayName = display_name or ""
        address.LocalPart = username or ""
        address.Domain = domain or ""
        address.Email = f"{address.LocalPart}@{address.Domain}" if address.Domain else address.LocalPart
        address.RawValue = raw_value or str(address)
        address.IsInternationalized = any(ord(character) > 127 for character in address.RawValue)
        return address

    def to_dict(self) -> dict:
        return {
            "display_name": self.DisplayName,
            "email": self.Email,
            "local_part": self.LocalPart,
            "domain": self.Domain,
            "raw_value": self.RawValue,
            "internationalized": self.IsInternationalized,
        }

    def to_header_value(self) -> str:
        return str(self)

    def __str__(self) -> str:
        """
        Returns a properly formatted email address string.

        If a display name is present, returns "Display Name <email@domain.com>",
        otherwise returns just the email address.

        :returns: Formatted email address string.
        """
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
    """RFC 5322/6854 address list retaining named and empty groups."""

    def __init__(self, raw_value: str = ""):
        self.RawValue = raw_value
        self.Items = []
        if raw_value:
            self.parse(raw_value)

    def parse(self, value: str):
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
        """Return a flattened, immutable mailbox view."""
        mailboxes = []
        for item in self.Items:
            if isinstance(item, AddressGroup):
                mailboxes.extend(item.addresses)
            else:
                mailboxes.append(item)
        return tuple(mailboxes)

    def __iter__(self):
        return iter(self.Items)

    def __len__(self):
        return len(self.Items)

    def __bool__(self):
        return bool(self.Items) or bool(self.RawValue)

    def to_header_value(self) -> str:
        values = []
        for item in self.Items:
            if isinstance(item, AddressGroup):
                members = ", ".join(address.to_header_value() for address in item.addresses)
                values.append(f"{item.display_name}: {members};")
            else:
                values.append(item.to_header_value())
        return ", ".join(values)

    def to_dict(self) -> list[dict]:
        result = []
        for item in self.Items:
            if isinstance(item, AddressGroup):
                result.append({"type": "group", **item.to_dict()})
            else:
                result.append({"type": "mailbox", **item.to_dict()})
        return result

    def __str__(self) -> str:
        return self.to_header_value()
