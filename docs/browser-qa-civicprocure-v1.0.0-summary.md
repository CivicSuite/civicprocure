# Browser QA - CivicProcure v1.0.0

Date: 2026-05-09

## Scope

- Public module UI at `GET /civicprocure`
- Documentation landing page at `docs/index.html`
- Desktop viewport: 1440x1000
- Mobile viewport: 390x900

## Evidence

- Public UI desktop screenshot: `docs/browser-qa-civicprocure-v1.0.0-desktop.png`
- Public UI mobile screenshot: `docs/browser-qa-civicprocure-v1.0.0-mobile.png`
- Docs desktop screenshot: `docs/browser-qa-docs-index-v1.0.0-desktop.png`
- Docs mobile screenshot: `docs/browser-qa-docs-index-v1.0.0-mobile.png`

## Results

- Browser console: no console messages or page errors on all checked pages.
- Desktop and mobile public UI render the `v1.0.0 procurement support + staff review queues` badge.
- Desktop and mobile docs render the `Shipping v1.0.0` badge.
- Keyboard/focus: first `Tab` reaches the public UI skip link; docs focus reaches the repository link.
- Copy review: public and docs surfaces clearly state that CivicProcure does not evaluate vendors, award contracts, make award decisions, submit procurements, provide legal advice, call live LLMs/live vendor portals, or replace the procurement system of record.
- UI states: static public/docs surfaces have no async loading state; success/status content is visible; empty/error/partial states are covered through API tests for persistence and staff queue configuration failures.

## Runtime Check

`GET /health` returned:

```json
{"status":"ok","service":"civicprocure","version":"1.0.0","civiccore_version":"1.0.0"}
```
