import json
from .Enumerations import DispositionType


class ContentDisposition:
    """
    A class to represent the Content-Disposition header of a MIME entity.

    This class parses and stores information from the Content-Disposition header,
    which indicates how content should be presented (as attachment or inline)
    and includes metadata such as filename, dates, and size.
    """
    def __init__(self):
        self.DispositionType: DispositionType = DispositionType.ATTACHMENT
        """Specifies whether the content should be displayed inline or as an attachment."""
        self.FileName = ""
        """The suggested filename for the MIME entity when saved to disk."""
        self.CreationDate = ""
        """RFC 2822 formatted date when the MIME entity was originally created."""
        self.ModificationDate = ""
        """RFC 2822 formatted date when the MIME entity was last modified."""
        self.Size = 0
        """Size of the MIME entity content in bytes."""

    def parse(self, ContentDispositionString: str):
        """
        Parses a Content-Disposition header string and populates the object's properties.

        This method extracts disposition type (inline/attachment) and associated parameters
        like filename, size, creation-date, and modification-date from the header string.

        :param ContentDispositionString: The Content-Disposition header value to parse.
        :returns: None - modifies the object's properties in place.
        """
        ContentDispositionString = ContentDispositionString.strip()
        if ContentDispositionString.find(";") != -1:
            ContentDispositionValues = ContentDispositionString.split(";")
            if (ContentDispositionValues[0].strip()).lower() == "inline":
                self.DispositionType = DispositionType.INLINE
            else:
                self.DispositionType = DispositionType.ATTACHMENT
            for index in range(1, len(ContentDispositionValues)):
                Current_Value = ContentDispositionValues[index]
                index_one = Current_Value.find("\"")
                if index_one == -1:
                    key = Current_Value.split("=")[0]
                    value = Current_Value.split("=")[1]
                else:
                    key = Current_Value[0:index_one]
                    key = key.strip("=")
                    Current_Value = Current_Value.replace(key + "=\"", "")
                    index_two = Current_Value.find("\"")
                    value = Current_Value[0:index_two]

                if key.lower().strip() == "filename":
                    self.FileName = value.strip()
                elif key.lower().strip() == "size":
                    self.Size = int(value.strip())
                elif key.lower().strip() == "creation-date":
                    self.CreationDate = value.strip()
                elif key.lower().strip() == "modification-date":
                    self.ModificationDate = value.strip()
                else:
                    continue
        else:
            self.DispositionType = ContentDispositionString.strip()

    def __str__(self) -> str:
        """
        Returns a JSON string representation of the ContentDisposition object.

        This method converts all properties into a dictionary and serializes it
        as a JSON string for easy debugging and logging purposes.

        :returns: JSON string containing all ContentDisposition properties.
        """
        return_data = dict()
        return_data.update({
            "Disposition-Type": self.DispositionType.name,
            "File-Name": self.FileName,
            "Creation-Date": self.CreationDate,
            "Modification-Date": self.ModificationDate,
            "Size": self.Size
        })

        return json.dumps(return_data)
