# Documentation development

The documentation portal uses Material for MkDocs, mike, and mkdocstrings.
Documentation dependencies are pinned separately from the library so the
EMLMailReader runtime remains dependency-free.

## Version scope

The portal publishes documentation by major release line:

- v1 documents the API released as EMLMailReader 1.0.4.
- v2 will document the Improvements work and become the default documentation
  when EMLMailReader 2.0.0 is released.

Changes on this branch must describe v1 behavior. Do not copy v2 APIs or
examples into the v1 portal.

## Local preview

Install the package and documentation tools:

```bash
mise run setup
mise run docs-setup
```

Start the local development server:

```bash
mise run docs-serve
```

MkDocs prints the local preview URL and rebuilds the portal when a source file
changes.

To preview the versions already published to the local `gh-pages` branch, run:

```bash
mise run docs-versioned-serve
```

## Strict build

Run the same strict validation used in CI:

```bash
mise run docs-build
```

The generated `site/` directory is ignored and must not be committed.

## Authoring rules

- Keep conceptual explanations and examples in `docs/`.
- Keep API behavior in source docstrings and expose it through
  the pages under `docs/reference/`.
- Add every user-facing page to the navigation in `mkdocs.yml`.
- Use repository-relative Markdown links.
- Run the strict documentation build before handing off a documentation
  change.

## Versioned publishing

Authored documentation stays with the matching library source. Generated HTML
for all supported versions is stored on the `gh-pages` branch:

- `docs/v1-portal` is the maintenance source for the v1 documentation.
- `docs/v2-portal` will be based on the v2 implementation.
- `gh-pages` is generated output and must not be edited manually.

Publishing v1 writes the site to `/v1/`, assigns the `stable` and `latest`
aliases, and makes `latest` the portal default:

```bash
mise run docs-deploy-v1
```

The publishing workflow performs the same mike deployment after a successful
push build on `docs/v1-portal`, packages the complete version store as a Pages
artifact, and deploys it through GitHub's official Pages action. It can also be
run manually. Pull requests use a separate read-only workflow that runs the
strict build.

Repository administrators must select **GitHub Actions** as the publishing
source under **Settings → Pages**. This is a one-time repository setting; the
workflow handles later portal deployments.

When v2 is released, publish it under `/v2/` and move `stable` and `latest` to
v2. The generated v1 snapshot remains available and selectable.

## Maintaining v1

Make v1 corrections on `docs/v1-portal`, validate them locally, and open a
pull request. Do not merge v2 implementation or documentation into this branch.
Republishing v1 replaces only the generated `/v1/` directory; other published
versions remain untouched.
