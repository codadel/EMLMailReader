# Install EMLMailReader v2

## Requirements

- Python 3.12 or newer
- no required runtime packages outside the standard library

Create and activate a virtual environment before installing the library:

=== "macOS or Linux"

    ```console
    python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install "emlmailreader>=2,<3"
    ```

=== "Windows PowerShell"

    ```powershell
    py -3.12 -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install "emlmailreader>=2,<3"
    ```

Pin the major version for production analytics pipelines so a future breaking
release cannot change parsed records unexpectedly.

## Verify the public API

```console
python -c "from EMLMailReader import MailReader, ParsingMode; print(ParsingMode.MODERN.value)"
```

The command should print `modern`.

## Type checking

The package includes a `py.typed` marker, so MyPy and other PEP 561-aware tools
can inspect its inline annotations without a separate stub package.

```python
from EMLMailReader import MailReader, RxMailMessage

message: RxMailMessage = MailReader().parse_bytes(
    b"From: alice@example.com\r\nSubject: Example\r\n\r\nHello"
)
```

Continue with [Parse your first message](first-email.md).
