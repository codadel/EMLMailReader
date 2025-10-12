# Logger

## Overview

The `Logger` class provides configurable logging functionality for the EMLMailReader library. It supports different log levels, multiple output formats, and can write to both console and file outputs. The class is designed to help track email parsing operations and troubleshoot issues during processing.

## Class Definition

```python
class Logger:
    """
    Provides configurable logging functionality for email parsing operations.

    This class manages logging output for the EMLMailReader library, supporting
    different log levels, output formats, and destinations. It helps track parsing
    operations and provides debugging information when processing email messages.
    """
```

## Constructor

### `__init__(self, enable_logging: bool = True, log_level: LoggingLevel = LoggingLevel.INFO, include_timestamp: bool = True, include_level: bool = True, output_to_console: bool = True, log_file_path: str = None)`

Creates a new Logger instance with the specified configuration.

**Parameters:**
- `enable_logging` (bool): Whether logging is enabled (default: True)
- `log_level` (LoggingLevel): Minimum log level to output (default: LoggingLevel.INFO)
- `include_timestamp` (bool): Whether to include timestamps in log messages (default: True)
- `include_level` (bool): Whether to include log level in messages (default: True)
- `output_to_console` (bool): Whether to output logs to console (default: True)
- `log_file_path` (str): Optional file path for log output (default: None)

**Example:**
```python
from EMLMailReader import Logger, LoggingLevel

# Basic logger
logger = Logger()

# Logger with file output
file_logger = Logger(
    log_level=LoggingLevel.DEBUG,
    log_file_path="email_parsing.log"
)

# Console-only logger without timestamps
console_logger = Logger(
    include_timestamp=False,
    output_to_console=True,
    log_file_path=None
)
```

## Properties

### `enabled` (bool)
Whether logging is currently enabled. Can be read and modified.

### `log_level` (LoggingLevel)
Current minimum log level for output. Can be read and modified.

### `include_timestamp` (bool)
Whether timestamps are included in log messages. Can be read and modified.

### `include_level` (bool)
Whether log levels are included in messages. Can be read and modified.

### `output_to_console` (bool)
Whether logs are output to console. Can be read and modified.

### `log_file_path` (str)
Current log file path, if any. Can be read and modified.

## Methods

### `log(self, level: LoggingLevel, message: str) -> None`

Logs a message at the specified level if it meets the current log level threshold.

**Parameters:**
- `level` (LoggingLevel): The log level for this message
- `message` (str): The message to log

**Example:**
```python
from EMLMailReader import Logger, LoggingLevel

logger = Logger(log_level=LoggingLevel.DEBUG)

logger.log(LoggingLevel.DEBUG, "Parsing email headers")
logger.log(LoggingLevel.INFO, "Successfully parsed email message")
logger.log(LoggingLevel.WARNING, "Attachment encoding not recognized")
logger.log(LoggingLevel.ERROR, "Failed to parse malformed email")
```

### `debug(self, message: str) -> None`

Logs a debug-level message. Used for detailed tracing of operations.

**Parameters:**
- `message` (str): Debug message to log

### `info(self, message: str) -> None`

Logs an info-level message. Used for general operational information.

**Parameters:**
- `message` (str): Info message to log

### `warning(self, message: str) -> None`

Logs a warning-level message. Used for non-critical issues that should be noted.

**Parameters:**
- `message` (str): Warning message to log

### `error(self, message: str) -> None`

Logs an error-level message. Used for serious issues that affect processing.

**Parameters:**
- `message` (str): Error message to log

## Usage Examples

### Basic Logging Setup

```python
from EMLMailReader import Logger, LoggingLevel, MailReader

def parse_email_with_logging(eml_file_path):
    """Parse an email file with comprehensive logging."""

    # Set up logger for this operation
    logger = Logger(
        log_level=LoggingLevel.INFO,
        include_timestamp=True,
        log_file_path="email_parsing.log"
    )

    logger.info(f"Starting to parse email: {eml_file_path}")

    try:
        # Create parser with the logger
        parser = MailReader(logger=logger)

        logger.debug("MailReader instance created")

        # Parse the email
        message = parser.parse_eml_file(eml_file_path)

        if message:
            logger.info(f"Successfully parsed email from: {message.mail_from}")
            logger.info(f"Subject: {message.subject}")
            logger.info(f"Attachments: {len(message.attachments)}")

            # Log attachment details
            for i, attachment in enumerate(message.attachments):
                logger.debug(f"Attachment {i+1}: {attachment.file_name} ({attachment.file_size_readable})")
        else:
            logger.error("Failed to parse email - no message returned")

    except Exception as e:
        logger.error(f"Exception during email parsing: {str(e)}")
        raise

    logger.info("Email parsing completed")
    return message

# Usage
message = parse_email_with_logging("test_email.eml")
```

### Multi-Level Logging Configuration

```python
from EMLMailReader import Logger, LoggingLevel

class EmailProcessingLogger:
    """Enhanced logging for email processing with multiple loggers."""

    def __init__(self, base_log_path="email_processing"):
        """Set up multiple loggers for different purposes."""

        # General operations logger
        self.general_logger = Logger(
            log_level=LoggingLevel.INFO,
            log_file_path=f"{base_log_path}_general.log",
            output_to_console=True
        )

        # Debug logger (file only, very verbose)
        self.debug_logger = Logger(
            log_level=LoggingLevel.DEBUG,
            log_file_path=f"{base_log_path}_debug.log",
            output_to_console=False
        )

        # Error logger (separate error file)
        self.error_logger = Logger(
            log_level=LoggingLevel.ERROR,
            log_file_path=f"{base_log_path}_errors.log",
            output_to_console=True
        )

    def log_operation_start(self, operation, details=""):
        """Log the start of an operation."""
        message = f"Starting {operation}"
        if details:
            message += f": {details}"

        self.general_logger.info(message)
        self.debug_logger.debug(f"[START] {message}")

    def log_operation_end(self, operation, success=True, details=""):
        """Log the end of an operation."""
        status = "completed" if success else "failed"
        message = f"Operation {operation} {status}"
        if details:
            message += f": {details}"

        if success:
            self.general_logger.info(message)
        else:
            self.error_logger.error(message)

        self.debug_logger.debug(f"[END] {message}")

    def log_processing_stats(self, stats_dict):
        """Log processing statistics."""
        for key, value in stats_dict.items():
            self.general_logger.info(f"Stats - {key}: {value}")
            self.debug_logger.debug(f"[STATS] {key}: {value}")

# Usage example
def process_email_batch(email_files):
    """Process multiple emails with comprehensive logging."""

    proc_logger = EmailProcessingLogger("batch_processing")

    proc_logger.log_operation_start("batch_processing", f"{len(email_files)} files")

    stats = {
        'total_files': len(email_files),
        'successful': 0,
        'failed': 0,
        'total_attachments': 0
    }

    for email_file in email_files:
        try:
            proc_logger.log_operation_start("parse_file", email_file)

            # Parse email (with MailReader's logger)
            parser = MailReader(logger=proc_logger.debug_logger)
            message = parser.parse_eml_file(email_file)

            if message:
                stats['successful'] += 1
                stats['total_attachments'] += len(message.attachments)
                proc_logger.log_operation_end("parse_file", True, f"{len(message.attachments)} attachments")
            else:
                stats['failed'] += 1
                proc_logger.log_operation_end("parse_file", False, "No message returned")

        except Exception as e:
            stats['failed'] += 1
            proc_logger.log_operation_end("parse_file", False, str(e))

    proc_logger.log_processing_stats(stats)
    proc_logger.log_operation_end("batch_processing", stats['failed'] == 0)

    return stats

# Process a batch of emails
email_files = ["email1.eml", "email2.eml", "email3.eml"]
results = process_email_batch(email_files)
```

### Dynamic Log Level Management

```python
from EMLMailReader import Logger, LoggingLevel

class AdaptiveLogger:
    """Logger that adjusts log level based on error frequency."""

    def __init__(self):
        self.logger = Logger(log_level=LoggingLevel.INFO)
        self.error_count = 0
        self.warning_count = 0
        self.total_operations = 0
        self.error_threshold = 0.1  # 10% error rate

    def log_with_adaptation(self, level, message):
        """Log message and adapt log level based on error patterns."""

        self.total_operations += 1

        # Track error patterns
        if level == LoggingLevel.ERROR:
            self.error_count += 1
        elif level == LoggingLevel.WARNING:
            self.warning_count += 1

        # Log the message
        self.logger.log(level, message)

        # Adapt log level if needed
        if self.total_operations >= 10:  # Only adapt after some operations
            error_rate = self.error_count / self.total_operations

            if error_rate > self.error_threshold and self.logger.log_level != LoggingLevel.DEBUG:
                self.logger.log_level = LoggingLevel.DEBUG
                self.logger.warning("High error rate detected - switching to DEBUG level")
            elif error_rate <= self.error_threshold / 2 and self.logger.log_level == LoggingLevel.DEBUG:
                self.logger.log_level = LoggingLevel.INFO
                self.logger.info("Error rate normalized - switching back to INFO level")

    def get_stats(self):
        """Get current logging statistics."""
        return {
            'total_operations': self.total_operations,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'error_rate': self.error_count / max(1, self.total_operations),
            'current_log_level': self.logger.log_level.name
        }

# Usage
adaptive_logger = AdaptiveLogger()

# Simulate some operations with varying error rates
operations = [
    (LoggingLevel.INFO, "Operation 1 successful"),
    (LoggingLevel.INFO, "Operation 2 successful"),
    (LoggingLevel.ERROR, "Operation 3 failed"),
    (LoggingLevel.WARNING, "Operation 4 had minor issues"),
    (LoggingLevel.ERROR, "Operation 5 failed"),
    (LoggingLevel.ERROR, "Operation 6 failed"),
    (LoggingLevel.INFO, "Operation 7 successful"),
    (LoggingLevel.ERROR, "Operation 8 failed"),
    (LoggingLevel.INFO, "Operation 9 successful"),
    (LoggingLevel.INFO, "Operation 10 successful"),
]

for level, message in operations:
    adaptive_logger.log_with_adaptation(level, message)

print("Final stats:", adaptive_logger.get_stats())
```

### Custom Log Formatting

```python
from EMLMailReader import Logger, LoggingLevel
import json
from datetime import datetime

class CustomFormattedLogger:
    """Logger with custom output formats."""

    def __init__(self, format_type="standard"):
        self.format_type = format_type
        self.logger = Logger(
            include_timestamp=False,  # We'll handle formatting ourselves
            include_level=False,
            log_file_path="custom_format.log"
        )

    def log_formatted(self, level, message, context=None):
        """Log with custom formatting."""

        timestamp = datetime.now()

        if self.format_type == "json":
            log_entry = {
                "timestamp": timestamp.isoformat(),
                "level": level.name,
                "message": message,
                "context": context or {}
            }
            formatted_message = json.dumps(log_entry)

        elif self.format_type == "detailed":
            formatted_message = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {level.name:>7} | {message}"
            if context:
                formatted_message += f" | Context: {context}"

        elif self.format_type == "compact":
            formatted_message = f"{timestamp.strftime('%H:%M:%S')} {level.name[0]} {message}"

        else:  # standard
            formatted_message = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} [{level.name}] {message}"

        self.logger.log(level, formatted_message)

# Usage examples
def demo_custom_formatting():
    """Demonstrate different log formats."""

    # JSON format logger
    json_logger = CustomFormattedLogger("json")
    json_logger.log_formatted(
        LoggingLevel.INFO,
        "Email parsed successfully",
        {"file": "test.eml", "attachments": 3, "size": "1.2MB"}
    )

    # Detailed format logger
    detailed_logger = CustomFormattedLogger("detailed")
    detailed_logger.log_formatted(
        LoggingLevel.WARNING,
        "Unknown attachment type detected",
        {"type": "application/x-unknown", "filename": "data.bin"}
    )

    # Compact format logger
    compact_logger = CustomFormattedLogger("compact")
    compact_logger.log_formatted(LoggingLevel.DEBUG, "Processing MIME part 3/7")

demo_custom_formatting()
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
from EMLMailReader import Logger, LoggingLevel

def best_practice_logging_example():
    logger = Logger()

    # DEBUG: Detailed tracing for development
    logger.debug("Entering parseHeaders() method")
    logger.debug("Found Content-Type header: text/html")

    # INFO: General operational information
    logger.info("Successfully parsed email message")
    logger.info("Extracted 3 attachments from email")

    # WARNING: Concerning but non-fatal issues
    logger.warning("Unknown character encoding detected, using UTF-8 fallback")
    logger.warning("Attachment filename contains special characters")

    # ERROR: Serious problems that affect processing
    logger.error("Failed to decode Base64 attachment content")
    logger.error("Malformed email structure - missing required headers")
```

### 2. Use Context-Aware Logging

```python
def parse_with_context_logging(email_file, logger):
    """Parse email with context-aware logging."""

    context = {"file": email_file, "operation": "parse_email"}

    logger.info(f"[{context['operation']}] Starting parse of {context['file']}")

    try:
        # Parsing operations with context
        logger.debug(f"[{context['operation']}] Reading file contents")

        # ... parsing logic ...

        logger.info(f"[{context['operation']}] Successfully completed for {context['file']}")

    except Exception as e:
        logger.error(f"[{context['operation']}] Failed for {context['file']}: {str(e)}")
        raise
```

### 3. Log Performance Information

```python
import time

def performance_aware_logging(logger):
    """Example of logging with performance information."""

    start_time = time.time()

    logger.info("Starting email parsing operation")

    # ... processing ...

    elapsed = time.time() - start_time
    logger.info(f"Email parsing completed in {elapsed:.3f} seconds")

    if elapsed > 5.0:
        logger.warning(f"Slow parsing detected: {elapsed:.3f}s (threshold: 5.0s)")
```

## Related Classes

- [MailReader](MailReader.md) - Primary consumer of Logger for parsing operations
- [Enumerations](Enumerations.md) - Defines LoggingLevel enumeration
- [RxMailMessage](RxMailMessage.md) - May use Logger for processing operations
- [Exceptions](Exceptions.md) - Errors that should be logged
