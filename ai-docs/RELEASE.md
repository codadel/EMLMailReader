# Release process

The `Release package and documentation` GitHub Actions workflow publishes
`emlmailreader` and its matching major-version documentation from the
`release` branch.

## Version source of truth

The workflow uses the exact `[project].version` value in `pyproject.toml`. It
does not increment or otherwise modify that version.

Before merging a release into `release`, set an unused stable semantic version
such as `2.0.0`. The workflow derives the documentation version from its major
component:

| Package version | Documentation source | Mike version |
| --- | --- | --- |
| `1.0.4` | `docs/v1/` and `mkdocs.v1.yml` | `v1` |
| `2.0.0` | `docs/v2/` and `mkdocs.v2.yml` | `v2` |
| `2.1.3` | `docs/v2/` and `mkdocs.v2.yml` | `v2` |

Run this check locally to see what a release would select:

```bash
mise run release-metadata
```

The command fails if the version is not exactly `MAJOR.MINOR.PATCH` or if the
matching documentation directory or configuration is missing.

## Automated release flow

1. Merge or push the authorized release commit into `release`.
2. The workflow reads the package version, derives `vN`, and rejects an
   existing `vMAJOR.MINOR.PATCH` tag.
3. It runs Ruff formatting and lint checks, strict MyPy analysis, the complete
   test suite with branch coverage, and a strict build of the matching docs.
4. It builds the wheel and source distribution, uploads them as a workflow
   artifact, and tags the exact release commit.
5. PyPI Trusted Publishing publishes those distributions.
6. After PyPI succeeds, Mike rebuilds the matching documentation source,
   updates that major version on `gh-pages`, and points `latest` and `stable`
   to it. Other major versions remain untouched.
7. GitHub Pages deploys the complete `gh-pages` snapshot containing every
   published documentation version.
8. After package and documentation publication succeed, the workflow generates
   release notes, prepends the release to `changelog.md`, and creates a GitHub
   Release with the distributions attached.

The changelog commit contains `[skip release]`, preventing the workflow's own
commit from starting another publication.

## Repository configuration

### PyPI Trusted Publishing

Configure a trusted publisher for:

- PyPI project: `emlmailreader`
- GitHub owner: `codadel`
- GitHub repository: `EMLMailReader`
- Workflow filename: `release.yml`
- Environment: `pypi`

No `PYPI_API_TOKEN` secret is required. The `publish_package` job uses GitHub
Actions OIDC through `pypa/gh-action-pypi-publish`.

### GitHub Pages

Under **Settings → Pages**, select **GitHub Actions** as the source. Allow the
`release` branch to deploy through the `github-pages` environment.

The workflow also needs permission to push:

- the release tag;
- the generated changelog commit to `release`; and
- Mike's generated documentation commits to `gh-pages`.

If branch protection blocks GitHub Actions from making those changes, update
the repository rules before starting a release.

## Release safeguards

Version changes, merges into `release`, tags, workflow dispatches, and package
or documentation publishing require explicit user authorization. Do not
perform them as an incidental part of implementation or validation.

Before an authorized release:

1. Confirm the intended semantic version and release commit.
2. Run `mise run release-metadata`.
3. Run `mise run quality` and `mise run pre-commit`.
4. Verify `README.md` and the selected `docs/vN/` source against the shipped
   API.
5. Build and inspect the package distributions.
6. Confirm that the corresponding version does not already exist on PyPI or as
   a Git tag.

Release validation is check-only. A failed check terminates the workflow before
the tag or any publication is created.
