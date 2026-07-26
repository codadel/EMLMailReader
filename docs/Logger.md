# Logger

`Logger` is a static wrapper around Python's process-wide root logger.
`MailReader` uses it to report parser diagnostics and filesystem read failures.

Applications normally configure logging through the `MailReader` constructor.

## Configure through MailReader

```python
from EMLMailReader import LoggingMode, MailReader

console_reader = MailReader(logging_mode=LoggingMode.CONSOLE)

file_reader = MailReader(
    logging_mode=LoggingMode.FILE,
    TargetLoggingFolder="/existing/log/directory",
)
```

`LoggingMode.NONE` is the default and leaves logging unconfigured.

## `set_configuration()`

```python
Logger.set_configuration(
    logging_mode: LoggingMode,
    target_folder: str = "",
) -> str
```

### Console mode

```python
from EMLMailReader import Logger, LoggingMode

result = Logger.set_configuration(LoggingMode.CONSOLE)
assert result == ""
```

Configures the root logger at `DEBUG` level with this format:

```text
timestamp level logger-name message
```

### File mode

```python
log_path = Logger.set_configuration(
    LoggingMode.FILE,
    "/existing/log/directory",
)
print(log_path)
```

The target must already exist. The method creates a UTF-8 log named like:

```text
EMLMailReader_Logs_2026712_143055.log
```

It returns the complete log path. A missing or empty target raises
`FolderNotAvailableError`.

The filename has one-second timestamp precision. Reconfiguring file logging
more than once in the same second can select the same filename.

### None mode

```python
result = Logger.set_configuration(LoggingMode.NONE)
assert result == ""
```

No logging configuration is changed.

### Process-wide effect

Console and file modes call `logging.basicConfig(..., force=True)`. They replace
existing root handlers and affect the entire Python process, not only
EMLMailReader. Applications that need centralized logging control can keep
`LoggingMode.NONE` and configure Python logging themselves.

## `logentry()`

```python
Logger.logentry(message: str, logging_level: LoggingLevel) -> None
```

```python
from EMLMailReader import Logger
from EMLMailReader.Enumerations import LoggingLevel

Logger.logentry("Message parsed", LoggingLevel.INFO)
Logger.logentry("Message could not be read", LoggingLevel.ERROR)
```

Routing:

| Level | Python logging call |
| --- | --- |
| `LoggingLevel.INFO` | `logging.info()` |
| `LoggingLevel.ERROR` | `logging.error()` |
| `LoggingLevel.CRITICAL` | `logging.critical()` |
| `LoggingLevel.DEBUG` or another value | `logging.debug()` |

`LoggingLevel` is imported from `EMLMailReader.Enumerations`; it is not
re-exported from the package root.

## Related pages

- [MailReader](MailReader.md)
- [Enumerations](Enumerations.md)
- [Exceptions](Exceptions.md)
