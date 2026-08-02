# Documentation development

The portal uses Material for MkDocs, Mike, and mkdocstrings. Documentation
dependencies are pinned separately so the EMLMailReader runtime remains
dependency-free.

## Source layout

The maintained branches retain Markdown source for every major release:

```text
docs/v1/        EMLMailReader 1.x source
docs/v2/        EMLMailReader 2.x source
mkdocs.yml      shared theme and plugin configuration
mkdocs.v1.yml   v1 source directory and navigation
mkdocs.v2.yml   v2 source directory and navigation
```

The v1 source is archived. New implementation guidance belongs in `docs/v2/`.
Published HTML for all versions remains on `gh-pages` and must not be edited
manually.

## Local setup

```bash
mise run setup
mise run docs-setup
```

## Build and preview

The current version defaults to v2:

```bash
mise run docs-build
mise run docs-serve
```

Pass a major version when needed:

```bash
mise run docs-build v2
mise run docs-serve v2
```

To preview snapshots already stored on the local `gh-pages` branch:

```bash
mise run docs-versioned-serve
```

The generated `site/` directory is ignored and must not be committed.

## Authoring rules

- Keep each major release under its matching `docs/vN/` directory.
- Keep tutorials and task guidance separate from exact API reference pages.
- Generate signatures from source docstrings through mkdocstrings.
- Add every user-facing page to the matching `mkdocs.vN.yml` navigation.
- Use repository-relative Markdown links.
- Build the active major version strictly before committing.
- Do not rebuild v1 API pages against v2 code and treat the result as a new v1
  publication.

## Publishing model

The unified release workflow reads the exact package version from
`pyproject.toml`, derives its major version, builds the matching configuration,
publishes the package to PyPI, and then deploys that major-version
documentation through Mike and GitHub Pages.

For example, package version `2.0.1` selects `mkdocs.v2.yml`, updates `/v2/`,
and keeps `/v1/` unchanged. Stable releases move the `latest` and `stable`
aliases to the published major version.

The workflow does not infer or increment the next package version. Release
preparation must set the intended `MAJOR.MINOR.PATCH` value explicitly. Run
`mise run release-metadata` to validate the package-to-documentation mapping
without publishing anything.

Documentation is published only by `.github/workflows/release.yml`; there is no
separate branch-specific documentation deployment. See
[Release process](RELEASE.md) for the complete order and repository settings.

Repository administrators must keep **GitHub Actions** selected under
**Settings → Pages** and allow the `release` branch to deploy through the
`github-pages` environment.
