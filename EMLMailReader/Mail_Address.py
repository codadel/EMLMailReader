from .Text_Encoding import TextEncoding
from copy import deepcopy


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

    def parse(self, MailAddressString: str):
        """
        Parses an email address string and extracts the display name and email components.

        This method handles both simple email addresses and those with display names,
        automatically decoding any encoded header content in the display name portion.

        :param MailAddressString: Email address string to parse (e.g., "John Doe <john@example.com>").
        :returns: None - modifies the object's properties in place.
        """
        MailAddressString = MailAddressString.strip()
        if MailAddressString.find("<") == -1:
            self.Email = MailAddressString
        else:
            index = MailAddressString.find("<")
            name_value = MailAddressString[0:index].strip()
            name_value = name_value.replace("\"", "")
            self.DisplayName = TextEncoding.decode_header(name_value)
            indexOne = MailAddressString.find(">")
            self.Email = MailAddressString[index + 1:indexOne].strip()

    def __str__(self) -> str:
        """
        Returns a properly formatted email address string.

        If a display name is present, returns "Display Name <email@domain.com>",
        otherwise returns just the email address.

        :returns: Formatted email address string.
        """
        if self.DisplayName != str():
            return self.DisplayName + " <" + self.Email + ">"
        else:
            return self.Email


class MailAddressCollection:
    """
    A collection class to manage multiple MailAddress instances.

    This class provides a container for storing and manipulating lists of email addresses
    commonly found in email headers like To, Cc, Bcc, and Reply-To fields.
    """
    def __init__(self):
        self.__addresses = list[MailAddress]()
        """Private list containing MailAddress instances in the collection."""

    def append(self, address: MailAddress):
        """
        Adds a MailAddress instance to the end of the collection.

        :param address: MailAddress object to be added to the collection.
        :returns: None - modifies the collection in place.
        """
        self.__addresses.append(address)

    def __str__(self) -> str:
        """
        Returns a semicolon-separated string of all email addresses in the collection.

        This format is commonly used in email headers for multiple recipients.

        :returns: Semicolon-delimited string of formatted email addresses.
        """
        mail_addresses = list()
        for address in self.__addresses:
            mail_addresses.append(str(address))

        return ";".join(mail_addresses)

    def length(self) -> int:
        """
        Returns the number of MailAddress items in the collection.

        :returns: Integer count of MailAddress instances in the collection.
        """
        return len(self.__addresses)

    def export_as_list(self) -> list:
        """
        Exports the collection as a new list of MailAddress instances.

        This method creates a deep copy of the internal collection to prevent
        external modification of the collection's internal state.

        :returns: A new list containing deep copies of all MailAddress instances.
        """
        return deepcopy(self.__addresses)
