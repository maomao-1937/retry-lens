# Research and decision record

Source review: 2026-10-23 (Asia/Singapore). This is a small implementation hypothesis, not a validated market opportunity.

## Observed facts

- [Tenacity documentation](https://tenacity.readthedocs.io/en/stable/index.html) describes a Python retry library with stop and wait conditions. It is an alternative when the task is implementing retries.
- [AWS Builders' Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) discusses retry side effects and idempotency. Logged success counts alone cannot establish whether a service created duplicate effects.
- Locally implemented behavior: this CLI groups saved events and checks attempt ceilings, attempts after a logged success, repeated logged successes, and missing attempt ranges. See TESTING.md for test evidence.

## Inference and chosen boundary

A portable offline report may help someone review a saved log before changing a retry policy. This is a proposed use, not evidence of demand. Tenacity changes execution behavior; retry-lens only audits a bounded exported event format. Its gap status explicitly requests review instead of claiming a complete history.

## Alternatives and unknowns

Use Tenacity for retry execution and your existing logging/tracing system when you need timestamps or live correlation. A short local JSON script may be sufficient for one-time audits. Real-user adoption, willingness to pay, Star growth, production incident reduction, compatibility with arbitrary telemetry schemas, and large-log performance are unverified. No claim of novelty or superiority is made.
