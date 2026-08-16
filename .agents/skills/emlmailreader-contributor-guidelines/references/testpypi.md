# TestPyPI candidate publishing

The `Publish merged version to TestPyPI` workflow publishes an isolated release
candidate after a pull request is merged into `develop`. Closing a pull request
without merging it does not run the jobs, and direct feature-branch pushes do
not trigger the workflow.

## Version selection

`[project].version` in `pyproject.toml` remains the stable production target and
must use exactly `MAJOR.MINOR.PATCH`. The workflow reads that value and queries
TestPyPI for existing versions in the same release series. Documentation is not
read, built, or published by this workflow.

For a source version of `2.0.0`, candidate selection works as follows:

| Versions already on TestPyPI | Selected version |
| --- | --- |
| None for `2.0.0` | `2.0.0rc1` |
| `2.0.0rc1` | `2.0.0rc2` |
| `2.0.0rc1`, `2.0.0rc3` | `2.0.0rc4` |

The selected release candidate is written only to the temporary GitHub Actions
checkout before the package is installed and built. The workflow does not
commit the candidate version back to `develop`.

Candidate preparation fails before package publication when:

- the project version is not a stable semantic version;
- TestPyPI cannot be queried or returns invalid project metadata; or
- the final base version, such as `2.0.0`, already exists on TestPyPI.

Run the same selection check locally without changing `pyproject.toml`:

```bash
mise run test-release-metadata
```

## Automated flow

1. A pull request targeting `develop` is merged.
2. The workflow checks out the exact merged commit.
3. The metadata script selects and temporarily applies the next unused RC.
4. Ruff formatting and lint checks, MyPy, and the full coverage suite run.
5. The workflow builds a wheel and source distribution containing the RC
   version.
6. Only if every validation and build step succeeds, the dependent publish job
   receives GitHub OIDC permission and uses the `testpypi` environment to
   publish both artifacts through TestPyPI Trusted Publishing.

The publish job declares both `needs: validate_and_build` and an explicit
successful-result condition. Any metadata, formatting, linting, typing, test,
coverage, or package-build failure skips publication. The checks are repeated
after merge so the exact commit being uploaded is the commit that passed them.

This flow does not tag a commit, update the changelog, publish documentation,
create a GitHub Release, or publish anything to production PyPI. Those actions
remain exclusive to the `release` branch workflow.

## Install and verify a candidate

Use the exact candidate displayed in the workflow summary:

```bash
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --no-deps \
  emlmailreader==2.0.0rc1
```

The package has no runtime dependencies, so `--no-deps` keeps the test tied to
TestPyPI. Install the repository's agent skill separately from the exact commit
being evaluated; the skill is repository content and is not embedded in the
Python distribution.

## Repository configuration

The TestPyPI trusted publisher must match:

- TestPyPI project: `emlmailreader`
- GitHub owner: `codadel`
- GitHub repository: `EMLMailReader`
- Workflow filename: `test-publish.yml`
- Environment: `testpypi`

No API token is required. The publish job requests an OIDC identity token only
after validation and package building succeed.
