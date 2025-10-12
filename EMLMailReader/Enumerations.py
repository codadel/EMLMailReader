from enum import Enum


class TransferEncoding(Enum):
    """
    Enumeration representing different content transfer encoding methods for MIME entities.

    These encoding methods define how binary or non-ASCII content is represented
    in text-based email messages as specified in RFC 2045.
    """
    BASE64 = 1
    """Base64 encoding for binary data and non-ASCII text."""
    SEVEN_BIT = 2
    """7-bit ASCII encoding (default, no encoding needed)."""
    EIGHT_BIT = 3
    """8-bit encoding for extended ASCII characters."""
    QUOTED_PRINTABLE = 4
    """Quoted-printable encoding for mostly ASCII text with occasional non-ASCII characters."""


class EntityType(Enum):
    """
    Enumeration representing different types of MIME entities found in email messages.

    This classification helps determine how content should be processed and displayed.
    """
    ATTACHMENT = 1
    """Binary files or documents attached to the email."""
    TEXT = 2
    """Plain text or HTML content that forms the email body."""
    MIME_PART = 3
    """Container for other MIME parts (multipart entities)."""


class DispositionType(Enum):
    """
    Enumeration representing content disposition types for MIME entities.

    This indicates how the receiving client should handle and display the content.
    """
    ATTACHMENT = 1
    """Content should be treated as a separate file attachment."""
    INLINE = 2
    """Content should be displayed inline within the message body."""


class LoggingLevel(Enum):
    """
    Enumeration defining different severity levels for logging messages.

    These levels help categorize log entries by importance and facilitate filtering.
    """
    DEBUG = 1
    """Detailed diagnostic information for troubleshooting."""
    INFO = 2
    """General informational messages about normal operation."""
    ERROR = 3
    """Error conditions that don't prevent continued operation."""
    CRITICAL = 4
    """Serious errors that may cause the application to terminate."""


class LoggingMode(Enum):
    """
    Enumeration defining different output destinations for logging messages.

    This controls where log messages are written during EML file processing.
    """
    CONSOLE = 1
    """Log messages are printed to the console/terminal."""
    FILE = 2
    """Log messages are written to a log file."""
    NONE = 3
    """Logging is disabled (no output generated)."""
