#!/usr/bin/env python3
"""Audit saved retry events without executing requests."""
import argparse
import json
import io
import math
from pathlib import Path
import sys

MAX_BYTES = 16 * 1024 * 1024
MAX_ROWS = 100_000

class Invalid(ValueError):
    pass

class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'error: invalid arguments; use --help\n')

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise Invalid('duplicate JSON key')
        result[key] = value
    return result

def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise Invalid('nonfinite JSON number')
    return result

def strict(text):
    return json.loads(text, object_pairs_hook=pairs, parse_float=number,
                      parse_constant=lambda _: (_ for _ in ()).throw(Invalid('nonfinite JSON number')))

def analyze(path, max_attempts):
    if path.stat().st_size > MAX_BYTES:
        raise Invalid('input exceeds 16 MiB')
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise Invalid('input exceeds 16 MiB')
    if not raw:
        raise Invalid('input has no events')
    rows = [row.decode('utf-8') for row in io.BytesIO(raw)]
    if len(rows) > MAX_ROWS:
        raise Invalid('too many events')
    groups = {}
    for line, text in enumerate(rows, 1):
        if len(text.encode('utf-8')) > 1024 * 1024:
            raise Invalid('event exceeds 1 MiB')
        try:
            event = strict(text)
            if not isinstance(event, dict):
                raise Invalid('event must be an object')
            op, attempt, status, duration = (event[k] for k in ('operation_id', 'attempt', 'status', 'duration_ms'))
            if not isinstance(op, str) or not op or len(op) > 512:
                raise Invalid('invalid operation_id')
            if type(attempt) is not int or not 1 <= attempt <= 1_000_000_000:
                raise Invalid('attempt must be a positive integer <= 1000000000')
            if status not in ('success', 'failure'):
                raise Invalid('invalid status')
            if type(duration) not in (int, float) or duration < 0 or not math.isfinite(duration):
                raise Invalid('invalid duration_ms')
            attempts = groups.setdefault(op, {})
            if attempt in attempts:
                raise Invalid('duplicate attempt within operation')
            attempts[attempt] = (status, duration)
        except (ValueError, KeyError, TypeError, OverflowError, RecursionError):
            raise Invalid(f'invalid event at line {line}') from None
    operations = []
    has_findings = has_review = False
    for op, events in sorted(groups.items()):
        ordered = sorted(events)
        successes = [a for a in ordered if events[a][0] == 'success']
        findings = []
        if max(ordered) > max_attempts:
            findings.append('max_attempts_exceeded')
        if successes and any(a > successes[0] for a in ordered):
            findings.append('attempted_after_success')
        if len(successes) > 1:
            findings.append('repeated_success')
        gaps = []
        previous = 0
        for attempt in ordered:
            if attempt > previous + 1:
                gaps.append([previous + 1, attempt - 1])
            previous = attempt
        duration = sum(events[a][1] for a in ordered)
        if not math.isfinite(duration):
            raise Invalid('duration total exceeds finite numeric range')
        has_findings |= bool(findings)
        has_review |= bool(gaps)
        operations.append(dict(operation_id=op, attempts=len(ordered), attempt_numbers=ordered,
                               success_count=len(successes), duration_ms=duration,
                               findings=findings, missing_attempt_ranges=gaps,
                               review=['incomplete_attempt_sequence'] if gaps else []))
    return dict(status='findings' if has_findings else 'review' if has_review else 'clean',
                event_count=len(rows), operation_count=len(operations), operations=operations)

def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--max-attempts', type=int, default=3, help='largest allowed attempt number (default: 3)')
    parser.add_argument('--format', choices=('json', 'text'), default='text')
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.max_attempts <= 1_000_000_000:
            raise Invalid('max-attempts must be 1..1000000000')
        result = analyze(args.input, args.max_attempts)
        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        else:
            print(f"{result['status']}: {result['event_count']} events, {result['operation_count']} operations")
            for op in result['operations']:
                print(json.dumps(op, ensure_ascii=True, allow_nan=False))
        return int(result['status'] != 'clean')
    except (OSError, ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        message = str(exc) if isinstance(exc, Invalid) else 'unable to read or parse input'
        print('error: ' + message, file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
