# Documentation and schema versions

The repository retains source documentation for every supported major release:

```text
docs/v1/  EMLMailReader 1.x
docs/v2/  EMLMailReader 2.x
```

The release workflow builds only the folder matching the package's major
version. Mike publishes that build beside existing versions on GitHub Pages.

## Stable URLs

Use a major-version URL when reproducibility matters:

```text
https://codadel.github.io/EMLMailReader/v2/
```

Use `/latest/` when documentation should follow the current stable package.

## Package and schema versions

The package follows semantic versioning. The canonical exported record also
contains `schema_version`, which identifies the shape of `to_dict()` and
`export_as_json()` independently from patch releases.

EMLMailReader 2.x currently emits schema version `2`.
