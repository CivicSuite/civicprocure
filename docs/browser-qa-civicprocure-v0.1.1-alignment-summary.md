# CivicProcure v0.1.1 Browser QA

Date: 2026-04-28

Scope:

- `docs/index.html` landing page after v0.1.1 / civiccore 0.3.0 alignment.
- Generated public UI from `civicprocure.public_ui.render_public_lookup_page()`.

Evidence:

- `browser-qa-civicprocure-v0.1.1-alignment-desktop.png` - docs landing page at 1440px.
- `browser-qa-civicprocure-v0.1.1-alignment-mobile.png` - docs landing page at 390px.
- `browser-qa-civicprocure-public-ui-v0.1.1-desktop.png` - public UI at 1440px.
- `browser-qa-civicprocure-public-ui-v0.1.1-mobile.png` - public UI at 390px.

Findings:

- Version labels show v0.1.1.
- CivicCore dependency language shows `civiccore==0.3.0`.
- Public-facing capability boundary remains honest: no vendor evaluation, contract awards, legal advice, live LLM calls, submissions, or procurement system-of-record replacement.
- Mobile screenshots render without right-edge clipping.
