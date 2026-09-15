# Contributing

The highest-value contribution is a falsification.

If an investigation overlooks a physical constraint, public dataset, publication-time issue, market rule or alternative explanation, open an issue with the smallest concrete counterexample you can provide. Corrections to published mysteries should preserve the original claim and record what changed.

For code changes:

```bash
uv sync --dev
./scripts/install-morpholog
./scripts/check
```

## Pre-commit hook

Run `ops/install-hooks` once per clone. It points `core.hooksPath` at
`ops/git-hooks`, whose `pre-commit` runs `ruff format --check`, `ruff check`,
`mypy` and `pytest -x` on every commit that touches Python, and `bash -n` on
staged scripts. `git commit -n` skips it for a deliberate exception.
