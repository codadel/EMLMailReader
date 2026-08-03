# Release process

The `Release package and documentation` GitHub Actions workflow runs only when
a pull request from `develop` into `release` is merged. It publishes
`emlmailreader` and its matching major-version documentation from that merged
release commit.

Test publications are handled separately after pull requests merge into
`develop`. See [TestPyPI candidate publishing](TESTPYPI.md) for automatic RC
selection and verification. The test workflow cannot tag releases, update the
changelog, deploy documentation, create a GitHub Release, or access the
production publishing environment.

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

1. Merge an authorized pull request from `develop` into `release`.
2. The read-only validation-and-build gate reads the package version, derives
   `vN`, rejects an existing `vMAJOR.MINOR.PATCH` tag, runs Ruff, MyPy, tests,
   branch coverage, and a strict matching-docs build, then builds and uploads
   the package distributions as an internal workflow artifact.
3. Only after validation succeeds, the OIDC-enabled PyPI job publishes the
   distributions.
4. Only after PyPI succeeds, Mike checks out the validated commit SHA, updates
   the matching major version on `gh-pages`, points `latest` and `stable` to
   it, and prepares the complete Pages artifact. Other major versions remain
   untouched.
5. Only after documentation publication succeeds, GitHub Pages deploys that
   artifact.
6. Only after validation, PyPI publication, and Pages deployment all succeed,
   the final job generates release notes, prepends the release to
   `changelog.md`, and creates the tag and GitHub Release at the exact validated
   commit with the distributions attached.

Each downstream job declares its prerequisite jobs with `needs` and explicitly
requires their results to be `success`. A failed or skipped prerequisite makes
all dependent release stages skip automatically. Write access and OIDC access
are granted only to the stages that need them. The release tag is not created
when package publication or documentation deployment fails.

The workflow listens for merged pull requests targeting `release`, not direct
pushes. Its changelog commit therefore does not start another release run.

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
