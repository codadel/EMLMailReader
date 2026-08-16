---
name: emlmailreader-contributor-guidelines
description: Repository contribution workflow for EMLMailReader. Use whenever changing this repository's Python parser, tests, documentation, packaging, CI, tooling, or release configuration; do not use it for application code that merely consumes the library.
---

# EMLMailReader contributor guidelines

Apply these instructions for every contribution to the EMLMailReader
repository. Keep the consumer-facing `use-emlmailreader` skill separate: it is
for developers writing applications with the installed library, not for
changing this library.

## Contribution workflow

1. Inspect `git status` before editing and preserve unrelated user changes.
2. Read only the references relevant to the requested change, then verify the
   current source, tests, workflows, and documentation before making edits.
3. Support Python 3.12 or newer and keep runtime code dependency-free unless a
   new dependency is explicitly approved.
4. Preserve the single canonical v2 API, its recursive schema, raw-source
   semantics, diagnostics, MIME behavior, and parser-limit contracts.
5. Keep unit tests filesystem-free. Put real EML and filesystem behavior in
   functional tests; keep packaging and release workflows in tooling tests.
6. Update exports, tests, and matching versioned public documentation together
   when public behavior changes.
7. Do not intentionally modify generated artifacts such as `.venv/`, coverage
   output, `.graphify*`, or `graphify-out/`.
8. Do not commit, push, tag, publish, or otherwise modify external state unless
   explicitly requested.

## Reference map

Load the reference that matches the task:

- [Local workspace setup](references/local-setup.md) for mise, the virtual
  environment, dependencies, and common commands.
- [Library implementation](references/library-implementation.md) for parser
  flow, the canonical data model, standards behavior, diagnostics, MIME
  handling, and resource limits.
- [Test instructions](references/test-instructions.md) for unit, functional,
  tooling, and coverage boundaries.
- [Code quality](references/quality.md) for Ruff, MyPy, pre-commit, and CI
  enforcement.
- [Documentation development](references/documentation.md) for versioned
  public docs and strict builds.
- [Release process](references/release.md) for versioning, branch flow,
  publication, and release safeguards.
- [TestPyPI candidates](references/testpypi.md) for RC selection and test
  publishing.

## Consumer-skill synchronization

Complete implementation and validation first. Then review
`skill/use-emlmailreader/`:

- Update its `SKILL.md` or references when the public API, observable parser
  behavior, diagnostics, parser limits, testing patterns, migration guidance,
  or privacy/safety expectations change.
- Leave it unchanged for purely internal, contributor-only, or release-only
  changes that do not affect library users.
- Never place repository setup, implementation architecture, release workflow,
  or maintainer-only rules in that consumer skill.

## Final validation

Run the smallest relevant checks during development. Before handoff, run:

```bash
mise run quality
mise run pre-commit
git diff --check
```

If mise is unavailable, use the equivalent commands in the testing and quality
references. Review the final diff and status, and confirm that generated files
and unrelated changes remain untouched.
