import os
from .Mail_Address import MailAddress
from .Mail_Attachment import MailAttachment
from .Text_Encoding import TextEncoding
from .Enumerations import TransferEncoding, EntityType, LoggingMode, LoggingLevel
from .Custom_Exceptions import InvalidEncodingError, FileMissingError, IncompleteHeaderError
from .Processing_Logs import Logger
from .Rx_Mail_Message import RxMailMessage


class MailReader:
    """
    Primary class for parsing and extracting information from EML (email) files.

    This class reads EML files, parses their MIME structure, extracts headers, body content,
    and attachments, then organizes everything into a structured RxMailMessage object.
    Supports multipart messages, various encodings, and comprehensive error handling.
    """
    def __init__(self, logging_mode: LoggingMode = LoggingMode.NONE, TargetLoggingFolder: str = str()):
        self.__Lines = list()
        """List containing all lines read from the EML file for processing."""
        self.__NextLineIndex = 0
        """Current position index for tracking which line to process next."""
        self.__NewLineCharacter = str()
        """The newline character sequence used in the current EML file."""
        self.__EndOfFile = "EOF"
        """Sentinel value returned when end of file is reached during parsing."""
        if logging_mode == LoggingMode.CONSOLE:
            Logger.set_configuration(LoggingMode.CONSOLE)
        elif logging_mode == LoggingMode.FILE:
            Logger.set_configuration(LoggingMode.FILE, TargetLoggingFolder)

    def __set_newline_value(self):
        """
        Determines and sets the newline character sequence used in the EML file.

        Different operating systems use different newline conventions (\\r\\n, \\r, \\n).
        This method examines the first line to detect the correct sequence for proper parsing.

        :returns: None - sets the internal newline character property.
        """
        first_line = self.__Lines[0]
        if first_line.endswith("\r\n"):
            self.__NewLineCharacter = "\r\n"
        elif first_line.endswith("\r"):
            self.__NewLineCharacter = "\r"
        else:
            self.__NewLineCharacter = "\n"

    def get_email(self, emlPath: str) -> RxMailMessage | None:
        """
        Parses an EML file and returns a structured representation of the email message.

        This is the main entry point for email parsing. It reads the file, processes
        all MIME parts recursively, and extracts headers, body, and attachments.

        :param emlPath: Complete file system path to the EML file to be parsed.
        :returns: RxMailMessage object containing all parsed email data, or None if parsing fails.
        """
        message = RxMailMessage()
        EmlFile = None
        try:
            if os.path.exists(emlPath):
                EmlFile = open(emlPath, "r")
                self.__Lines = EmlFile.readlines()
                EmlFile.close()
                self.__set_newline_value()
                self.__NextLineIndex = 0
                message = self.__process_mime_entity(message, str())
            else:
                raise FileMissingError(emlPath)
        except Exception as ex:
            Logger.logentry(f"An exception occurred while reading contents from EML file: {ex}", LoggingLevel.ERROR)
            message = None
        finally:
            if EmlFile is not None:
                EmlFile.close()

        return message

    def __process_mime_entity(self, message: RxMailMessage, ParentBoundary: str) -> RxMailMessage:
        """
        Recursively processes individual MIME parts within an email message.

        This method handles the parsing of MIME entities including headers, multipart boundaries,
        and content extraction. It properly handles nested multipart structures and builds
        a hierarchical representation of the email content.

        :param message: RxMailMessage object to populate with parsed data.
        :param ParentBoundary: Boundary string of the parent multipart entity (empty for top-level).
        :returns: Populated RxMailMessage object with parsed MIME entity information.
        """
        try:
            CompletedHeader = str()
            ParentBoundaryStart = "--" + ParentBoundary
            ParentBoundaryEnd = ParentBoundaryStart + "--"
            while True:
                line = self.__get_next_line()
                if line.startswith(" ") or line.startswith("\t"):
                    if CompletedHeader == str():
                        raise IncompleteHeaderError(line, self.__NextLineIndex)
                    else:
                        CompletedHeader = CompletedHeader + TextEncoding.decode_header(line.strip())
                elif line == str():
                    if CompletedHeader is not str():
                        self.__process_header(CompletedHeader, message)
                    Logger.logentry(f"Empty line found on row {self.__NextLineIndex} of EML File. Header processing completed for the current MIME entity.", LoggingLevel.INFO)
                    break
                else:
                    if CompletedHeader == str():
                        CompletedHeader = TextEncoding.decode_header(line.strip())
                    else:
                        self.__process_header(CompletedHeader, message)
                        CompletedHeader = TextEncoding.decode_header(line.strip())

            message.set_entity_type()
            if ParentBoundary == str() and message.ContentType.Boundary == str():
                message.IsMultiPart = False
                complete_body = str()
                line = self.__get_next_line()
                while line is not str() and line != self.__EndOfFile:
                    if complete_body == str():
                        complete_body = line
                    else:
                        complete_body = complete_body + self.__NewLineCharacter + line
                    line = self.__get_next_line()
                self.__parse_entity_body(message, complete_body)
            else:
                complete_body = str()
                message.IsMultiPart = True
                if message.ContentType.Boundary != str():
                    BoundaryFound = True
                    BoundaryStart = "--" + message.ContentType.Boundary
                    BoundaryEnd = BoundaryStart + "--"
                else:
                    BoundaryFound = False
                    BoundaryStart = str()
                    BoundaryEnd = str()
                while True:
                    line = self.__get_next_line()
                    if BoundaryFound and line == BoundaryStart:
                        message_child = self.__process_mime_entity(RxMailMessage(), message.ContentType.Boundary)
                        message.Children.append(message_child)
                        for attachment in message_child.Attachments.export_as_list():
                            message.Attachments.append(attachment)
                        message.Body = message_child.Body
                        if self.__get_last_line() == BoundaryStart:
                            self.__NextLineIndex = self.__NextLineIndex - 1
                    elif line == ParentBoundaryStart or line == ParentBoundaryEnd:
                        if not BoundaryFound:
                            self.__parse_entity_body(message, complete_body)
                        break
                    elif (BoundaryFound and line == BoundaryEnd) or line == self.__EndOfFile:
                        break
                    else:
                        if complete_body == str():
                            complete_body = line
                        else:
                            complete_body = complete_body + self.__NewLineCharacter + line
        except Exception as ex1:
            Logger.logentry(f"An exception occurred while processing the MIME Entity:{ex1}", LoggingLevel.ERROR)

        return message

    def __process_header(self, header: str, message: RxMailMessage) -> None:
        """
        Parses individual email headers and populates the appropriate message properties.

        This method recognizes standard email headers (From, To, Subject, etc.) and
        specialized MIME headers (Content-Type, Content-Disposition, etc.), properly
        decoding encoded content and handling multiple recipients.

        :param header: Complete header string including name and value.
        :param message: RxMailMessage object to populate with header information.
        :returns: None - modifies the message object in place.
        """
        try:
            header = header.strip()
            if header.strip().find(":") == -1:
                raise IncompleteHeaderError(header, self.__NextLineIndex)
            colon_index = header.strip().find(":")
            rValue = header[colon_index + 1:]
            rValue = rValue.strip()
            if header.lower().startswith("from"):
                mail_address = MailAddress()
                mail_address.parse(rValue)
                message.From = mail_address
            elif header.lower().startswith("to"):
                rValue = rValue.replace(",", ";")
                emails = rValue.split(";")
                for email in emails:
                    message.add_mail_address("To", email)
            elif header.lower().startswith("cc"):
                rValue = rValue.replace(",", ";")
                emails = rValue.split(";")
                for email in emails:
                    message.add_mail_address("Cc", email)
            elif header.lower().startswith("bcc"):
                rValue = rValue.replace(",", ";")
                emails = rValue.split(";")
                for email in emails:
                    message.add_mail_address("Bcc", email)
            elif header.lower().startswith("reply-to"):
                rValue = rValue.replace(",", ";")
                emails = rValue.split(";")
                for email in emails:
                    message.add_mail_address("ReplyTo", email)
            elif header.lower().startswith("message-id"):
                message.MessageID = rValue
            elif header.lower().startswith("mime-version"):
                message.MimeVersion = rValue
            elif header.lower().startswith("subject"):
                message.Subject = TextEncoding.decode_header(rValue)
            elif header.lower().startswith("date"):
                message.Date = rValue
            elif header.lower().startswith("content-type"):
                message.set_content_type(rValue)
            elif header.lower().startswith("content-transfer-encoding"):
                message.set_content_transfer_encoding(rValue)
            elif header.lower().startswith("content-description"):
                message.ContentDescription = rValue
            elif header.lower().startswith("content-disposition"):
                message.set_content_disposition(rValue)
            elif header.lower().startswith("content-id"):
                message.ContentID = rValue.lstrip("<").rstrip(">")
            else:
                lValue = (header.split(":")[0]).strip()
                message.Headers.update({lValue: rValue})
        except Exception as ex:
            Logger.logentry(f"An exception occurred while processing header '{header}': {ex}", LoggingLevel.ERROR)

    def __get_next_line(self) -> str:
        """
        Retrieves the next line from the EML file for processing.

        This method manages the sequential reading of file lines, handles newline character
        stripping, and returns an EOF marker when the end of file is reached.

        :returns: Next line content with newline characters removed, or EOF marker if file end reached.
        """
        NextLine = str()
        try:
            if self.__NextLineIndex < len(self.__Lines):
                NextLine = self.__Lines[self.__NextLineIndex]
                NextLine = NextLine.strip(self.__NewLineCharacter)
                self.__NextLineIndex = self.__NextLineIndex + 1
            else:
                NextLine = self.__EndOfFile
        except Exception as ex:
            Logger.logentry(f"An error occurred while fetching the next line to be processed: {ex}", LoggingLevel.ERROR)

        return NextLine

    def __get_last_line(self) -> str:
        """
        Retrieves the most recently processed line from the EML file.

        This method provides access to the previous line for boundary detection
        and parsing logic that needs to look back at processed content.

        :returns: Content of the last processed line with newline characters removed.
        """
        LastLine = str()
        try:
            LastLine = self.__Lines[self.__NextLineIndex - 1]
            LastLine = LastLine.strip(self.__NewLineCharacter)
        except Exception as ex:
            Logger.logentry(f"Exception occurred in get_last_line():> {ex}", LoggingLevel.ERROR)

        return LastLine

    def __parse_entity_body(self, message: RxMailMessage, complete_body: str):
        """
        Decodes and processes the body content of a MIME entity based on its transfer encoding.

        This method handles various content transfer encodings (Base64, Quoted-Printable, etc.)
        and determines whether content should be treated as text or as a file attachment based
        on the Content-Type header.

        :param message: RxMailMessage object to store the decoded content.
        :param complete_body: Raw encoded body content from the MIME entity.
        :returns: None - modifies the message object's Body or Attachments properties.
        """
        try:
            if message.ContentTransferEncoding == TransferEncoding.BASE64:
                complete_body = complete_body.replace(self.__NewLineCharacter, "")
                if message.ContentType.MediaType.lower().startswith("application") or message.ContentType.MediaType.lower().startswith("image"):
                    mail_attachment = MailAttachment()
                    mail_attachment.parse_values(TextEncoding.decode_base64_file(complete_body), message.ContentType, message.ContentDisposition, message.ContentID)
                    message.Attachments.append(mail_attachment)
                    message.Body = str()
                else:
                    message.Body = TextEncoding.decode_base64_string(complete_body, message.ContentType.Charset)
            elif message.ContentTransferEncoding == TransferEncoding.QUOTED_PRINTABLE:
                if message.EntityType == EntityType.TEXT:
                    message.Body = TextEncoding.decode_quoted_printable_string(complete_body, message.ContentType.Charset, False)
            elif message.ContentTransferEncoding == TransferEncoding.SEVEN_BIT:
                message.Body = complete_body
            elif message.ContentTransferEncoding == TransferEncoding.EIGHT_BIT:
                message.Body = complete_body
            else:
                raise InvalidEncodingError()
        except Exception as ex:
            Logger.logentry(f"An error occurred while parsing entity body: {ex}", LoggingLevel.ERROR)
