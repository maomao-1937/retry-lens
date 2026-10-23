# Validation record

Executed on 2026-10-23 (Asia/Singapore), Windows, CPython 3.11.15. This records the actual local run, not future CI or another operating system.

## Unit tests

```sh
python -m unittest discover -s tests -v
```

Exit 0; 14 tests discovered, 14 passed, 0 skipped, zero failures/errors.

## CLI examples and exit contracts

Each top-level checks.json entry was executed from this repository root with the current Python executable. All expected return codes matched; exit 1/2 rows are intentional negative cases. Generated outputs may be replaced on repeat runs as specified by the command.

| Arguments after python | Expected exit | Actual exit |
| --- | --- | --- |
| `retry_lens.py --help` | 0 | 0 |
| `retry_lens.py examples/clean.jsonl --format json` | 0 | 0 |
| `retry_lens.py examples/findings.jsonl --format json` | 1 | 1 |
| `retry_lens.py examples/review.jsonl --format json` | 1 | 1 |
| `retry_lens.py examples/invalid.jsonl` | 2 | 2 |

The test suite uses temporary directories and calls the root CLI directly. No network calls, package installation, credentials, or publication were needed.

## Limits of this evidence

Linux/macOS and other Python versions were not executed. No production workload, real-user adoption, performance benchmark, or hostile concurrent filesystem race has been validated. Re-run the commands on each intended environment.

Coverage includes unordered attempts, attempt ceilings, retry after success, repeated success, gaps requiring review, empty-log rejection, strict numeric/JSON validation, duplicate attempts, and CLI help.
