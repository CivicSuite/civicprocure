# CivicProcure v1.0.0 Release Gate

Date: 2026-05-09

## Scope

CivicProcure v1.0.0 productization for procurement support, staff review queues, review-required CivicClerk/CivicContracts context packets, adversarial local integration mocks, CivicCore v1.0.0 release-wheel alignment, docs, tests, browser QA, and release artifacts.

## Internal Careful-Work Evidence

1. Read callers/consumers: reviewed FastAPI routes, persistence repository, tests, release scripts, public UI, README/manual, docs landing page, CivicSuite unified spec, and previous v1 module patterns as read-only references.
2. Traced runtime context: verified stateless behavior when `CIVICPROCURE_WORKPAPER_DB_URL` is unset and staff-gated behavior when `CIVICPROCURE_WORKPAPER_DB_URL` plus `CIVICPROCURE_STAFF_API_KEY` are set.
3. Pattern search: searched existing v1 modules for staff queue, integration mock, CivicCore wheel, and release-gate patterns.
4. Data contract changed: added staff review queue records, review summaries, context packet fields, mock validation payloads, and `staff_review_id` response fields on persisted RFP drafts and award packets.
5. Blast radius: limited to CivicProcure package, tests, docs, release scripts, CI workflow, and generated QA/build artifacts.
6. Re-read changed files: diff and test passes checked route, persistence, docs, and release-script contracts before commit.
7. Code/data/render path: `POST /api/v1/civicprocure/rfps/draft` creates a deterministic RFP outline; with persistence configured it creates a staff queue item; staff-only headers allow list/update/summary; browser UI and docs describe the workflow and boundaries.
8. State consumption: queue records are persisted, listed, summarized, updated, and asserted through tests; context/mock payloads are exposed through API routes and tests.
9. Five-lens self-audit: product boundary, data contract, security/staff gate, docs truth, and release verification were checked before commit.

## Verification

```text
python -m pytest -q
23 passed, 1 warning

python -m ruff check .
All checks passed!

bash scripts/verify-release.sh
VERIFY-RELEASE: PASSED
```

Full release verifier covered version synchronization, tests, documentation gate, placeholder import guard, Ruff, build artifacts, and SHA256SUMS generation.

## Browser QA

Evidence is recorded in `docs/browser-qa-civicprocure-v1.0.0-summary.md` with desktop/mobile screenshots for `/civicprocure` and `docs/index.html`. Browser console was clean on all checked pages.

## Release-Gate Findings

- Blocker: none.
- Critical: none.
- Residual risk: installer integration is still required before the module may be called fully v1.0.0 complete under the CivicSuite active pipeline rule. That will be handled as the required CivicSuite installer exception after this repo change is pushed and CI is green.
