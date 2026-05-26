# Release Process

This project publishes `emlmailreader` to PyPI from the `release` branch.

## Automated Release Flow

1. Merge or push the changes intended for release into the `release` branch.
2. The `Release to PyPI` GitHub Actions workflow runs the unittest suite.
3. If tests pass, the workflow increments the patch version in `pyproject.toml`.
4. The workflow commits the version bump with a `[skip release]` marker, tags it as `vX.Y.Z`, builds the package, and publishes it to PyPI.

The `[skip release]` marker prevents the workflow's own version-bump commit from creating another release.

## PyPI Trusted Publishing Setup

Before the first automated release, configure PyPI Trusted Publishing for this project:

- PyPI project: `emlmailreader`
- GitHub owner: `codadel`
- GitHub repository: `EMLMailReader`
- Workflow filename: `release.yml`
- Environment: `pypi`

No `PYPI_API_TOKEN` GitHub secret is required. The publish job uses GitHub Actions OIDC with `pypa/gh-action-pypi-publish`.

## Notes

- The workflow performs patch-only version bumps, for example `1.0.3` to `1.0.4`.
- The `release` branch must allow GitHub Actions to push the version-bump commit and tag using `GITHUB_TOKEN`.
- If branch protection requires pull requests or blocks workflow pushes, update the branch protection rules before relying on this release flow.
