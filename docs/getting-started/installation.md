# Installation

## Requirements

EMLMailReader 1.0.4 requires Python 3.12 or newer. It has no third-party runtime
dependencies.

Check your Python version:

```console
python --version
```

## Install the v1 release

Pin the major documentation to the matching package release:

```console
python -m pip install "emlmailreader==1.0.4"
```

Using a virtual environment keeps the installation separate from system
packages:

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install "emlmailreader==1.0.4"
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Verify the installation

```console
python -c "from EMLMailReader import MailReader; print(MailReader)"
```

The import package uses the capitalized name `EMLMailReader`, even though the
package installed from PyPI is named `emlmailreader`.

## Install from a checkout

Contributors can install the current checkout in editable mode:

```console
python -m pip install -e .
```

Documentation tooling is intentionally separate from the runtime package. Use
`mise run docs-setup` only when you are building this portal locally.

## Next step

Continue with [Parse your first email](first-email.md).
