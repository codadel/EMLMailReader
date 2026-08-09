"""Enumerations shared by message parsing, decoding, and logging."""

from enum import Enum


class TransferEncoding(str, Enum):
    """Classify standard MIME Content-Transfer-Encoding tokens."""

    BASE64 = "base64"
    """Base64 encoding for binary data and non-ASCII text."""
    SEVEN_BIT = "7bit"
    """7-bit ASCII encoding (default, no encoding needed)."""
    EIGHT_BIT = "8bit"
    """8-bit encoding for extended ASCII characters."""
    QUOTED_PRINTABLE = "quoted-printable"
    """Quoted-printable encoding for mostly ASCII text with occasional non-ASCII characters."""
    BINARY = "binary"
    """Unencoded binary MIME content."""
    UNKNOWN = "unknown"
    """An extension or unrecognized content-transfer-encoding."""


class LoggingLevel(Enum):
    """Select the Python logging severity used by :class:`Logger`."""

    DEBUG = 1
    """Detailed diagnostic information for troubleshooting."""
    INFO = 2
    """General informational messages about normal operation."""
    ERROR = 3
    """Error conditions that don't prevent continued operation."""
    CRITICAL = 4
    """Serious errors that may cause the application to terminate."""


class LoggingMode(Enum):
    """Select whether parser diagnostics are disabled, logged, or written."""

    CONSOLE = 1
    """Log messages are printed to the console/terminal."""
    FILE = 2
    """Log messages are written to a log file."""
    NONE = 3
    """Logging is disabled (no output generated)."""
