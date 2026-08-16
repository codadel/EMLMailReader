# Agent instructions

These instructions apply to the entire repository. Keep public README content
brief; put detailed contributor guidance in the project-local contributor skill
instead.

## Always follow

- Inspect `git status` before editing and preserve unrelated user changes.
- Support Python 3.12 or newer. Keep runtime code dependency-free unless the
  user explicitly approves a new dependency.
- Preserve the single canonical v2 API. Do not reintroduce removed legacy
  projections, compatibility modes, duplicate attachment/address classes, or
  alternate serialization schemas.
- Keep unit tests filesystem-free. Real EML files and EML-related filesystem
  behavior belong in functional tests. Packaging and release filesystem
  workflows belong in tooling tests.
- Update package exports, tests, and versioned public documentation together
  when public behavior changes.
- Maintain more than 95% branch coverage for every library module and for the
  package overall.
- Do not intentionally edit generated artifacts such as `.venv/`,
  `.pytest_cache/`, `htmlcov/`, `*.egg-info/`, `.coverage`, `.graphify*`, or
  `graphify-out/`.
- Do not commit, push, tag, publish, or otherwise modify external state unless
  the user explicitly requests it.

## Contributor skill boundaries

- Use [.agents/skills/emlmailreader-contributor-guidelines/SKILL.md](.agents/skills/emlmailreader-contributor-guidelines/SKILL.md)
  for repository changes. Its references contain the detailed setup,
  implementation, testing, quality, documentation, release, and TestPyPI
  guidance.
- `skill/use-emlmailreader` is an end-user skill for developers writing code
  with the installed EMLMailReader library. Do not use it while changing this
  repository's source, tests, documentation, tooling, or workflows.
- After implementation and validation, update the user skill only when the
  public API or user-visible behavior, diagnostics, parser limits, testing
  patterns, migration guidance, or privacy/safety expectations changed. Keep
  contributor and release guidance out of that skill.

## Documentation sources

- `README.md` is the concise PyPI-facing overview: installation, a minimal
  example, documentation, license, and support only.
- `docs/v2/` and `mkdocs.v2.yml` are the current v2 public documentation.
- `docs/v1/` and `mkdocs.v1.yml` are the frozen v1.0.4 documentation. Never
  regenerate v1 pages against v2 code.
- The contributor skill's [documentation reference](.agents/skills/emlmailreader-contributor-guidelines/references/documentation.md)
  describes the versioned portal and authoring rules. Use
  `scripts/docs.py build vN` for a strict build and
  `scripts/docs.py serve vN` for a local preview.

## Read before changing

- [Contributor guidelines](.agents/skills/emlmailreader-contributor-guidelines/SKILL.md)
  and the relevant linked reference are required reading before repository
  changes.
- [Current public documentation](docs/v2/index.md) and [v1 documentation](docs/v1/index.md).

## Versioned documentation rules

- Keep v1 and v2 source trees in the repository together.
- A documentation change belongs in the matching `docs/vN/` tree and
  `mkdocs.vN.yml` navigation.
- The release metadata script selects the documentation major from
  `[project].version` in `pyproject.toml`; run `mise run release-metadata` to
  validate the mapping without publishing.
- The release workflow publishes only the matching major version through Mike
  and leaves other published major versions intact.

## Workflow triggers

- `quality.yml` and `docs.yml` run for pull requests targeting `develop`.
- `test-publish.yml` runs after a pull request is merged into `develop`. It
  selects the next unused release candidate, repeats quality checks, and
  publishes to TestPyPI only after validation succeeds. It does not build docs,
  create tags, update the changelog, or publish to production PyPI.
- `release.yml` runs only after a same-repository pull request from `develop`
  to `release` is merged. It validates and builds first, then publishes to
  PyPI, publishes the matching docs, deploys GitHub Pages, and finally records
  the changelog, tag, and GitHub Release. Direct pushes do not trigger it.

## Required validation

Run the smallest relevant checks while developing. Before handoff, run:

```bash
mise run quality
mise run pre-commit
git diff --check
```

If mise is unavailable after setup, use the equivalent pytest, Ruff, MyPy,
coverage, and pre-commit commands documented in the contributor skill's
[test instructions](.agents/skills/emlmailreader-contributor-guidelines/references/test-instructions.md)
and [quality reference](.agents/skills/emlmailreader-contributor-guidelines/references/quality.md).
