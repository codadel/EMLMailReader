# Documentation versions

The portal publishes one documentation snapshot for each supported major
release line.

## v1

The v1 documentation describes EMLMailReader 1.0.4. Its source is maintained on
the `docs/v1-portal` branch and its generated site is published under `/v1/`.

Corrections to v1 documentation must continue to describe v1 behavior. New v2
APIs and examples do not belong in this snapshot.

## v2

The v2 portal will be generated from the v2 implementation and published under
`/v2/`. When v2.0.0 becomes the stable release, the `latest` and `stable`
aliases will move to v2 while `/v1/` remains available.

## Stable links

Use a major-version URL when reproducibility matters:

```text
https://codadel.github.io/EMLMailReader/v1/
```

Use the portal root or `/latest/` when you want the current stable
documentation. The version selector switches between the published snapshots.
