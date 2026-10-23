# retry-lens

[![tests](https://github.com/maomao-1937/retry-lens/actions/workflows/tests.yml/badge.svg)](https://github.com/maomao-1937/retry-lens/actions/workflows/tests.yml)

Audit saved retry attempts before reviewing a retry policy. Python 3.11+; standard library only; offline CLI. It executes no requests and changes no input files.

## Quickstart

Run commands from this repository directory (Windows: `python`; systems using another launcher: `python3`). No installation is needed.

```sh
python retry_lens.py examples/clean.jsonl --format json
python retry_lens.py examples/findings.jsonl --max-attempts 3 --format json
python retry_lens.py examples/review.jsonl --format json
python -m unittest discover -s tests -v
```

The first command exits 0: the deliberately unordered rows become attempts `[1, 2]`. The second exits 1 with `attempted_after_success`, `repeated_success`, and `max_attempts_exceeded`. The third exits 1 with status `review`: missing attempts 1 through 2 are an incomplete log sequence requiring investigation.

## Input and interpretation

Each UTF-8 physical JSONL line is an object with `operation_id` (nonempty string, up to 512 characters), `attempt` (integer 1..1000000000), `status` (`success` or `failure`), and finite nonnegative numeric `duration_ms`. Extra fields are ignored. Boolean attempt/duration values, duplicate keys or attempts, blank lines, BOM, malformed JSON, NaN and infinities are rejected. Maximum input: 16 MiB, 100000 events, 1 MiB per line. Empty input is rejected with exit 2 because it supplies no events to audit.

Events group by operation and sort by attempt number, independent of line order. `--max-attempts` is the largest allowed attempt number, default 3. Output includes attempt numbers, count, success count, summed recorded duration, policy findings, and compact missing-attempt ranges. All-failure sequences can be clean: clean means no configured anomaly in the available events, not successful work. An operation ID must represent the same logical operation throughout the file.

| Exit | Meaning |
| --- | --- |
| 0 | No configured findings or sequence gaps |
| 1 | Findings, or gaps needing review |
| 2 | Invalid input, arguments, bounds, or file access |

## 中文快速开始

在仓库目录运行上面的命令，无需安装第三方包。将每次重试记录为一行 JSON，确保同一次业务操作使用相同的 `operation_id`，然后运行 `python retry_lens.py 你的日志.jsonl --format json`。返回码 0 表示当前记录未触发规则，1 表示发现异常或日志缺口，2 表示输入/参数错误。日志缺口标为 `review`，不能据此声称重试链完整；`success` 只是日志声明，无法证明服务端仅产生一次副作用。

## Scope

No timestamps, backoff schedules, latency percentiles, idempotency keys, live tracing, automatic policy changes, or proof of exactly-once effects. Duration totals cover logged attempts only. Reports include operation IDs; review them before sharing. See [RESEARCH.md](RESEARCH.md) for evidence and alternatives and [TESTING.md](TESTING.md) for actual validation. MIT license.
