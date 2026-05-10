"""Static public UI shell for CivicProcure v0.2.0."""

from __future__ import annotations


def render_public_lookup_page() -> str:
    """Render the public-facing CivicProcure sample page."""

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CivicProcure Procurement Support</title>
<style>
  :root { --ink:#19212b; --muted:#56606a; --paper:#fffaf2; --blue:#244f73; --green:#2f654c; --gold:#d7aa45; --line:#d8c7a5; }
  * { box-sizing: border-box; }
  body { margin:0; color:var(--ink); font-family:"Aptos","Segoe UI",sans-serif; background:linear-gradient(135deg,#fff7e6,#edf7ef); }
  .skip-link { position:absolute; left:1rem; top:-4rem; background:var(--ink); color:white; padding:.7rem 1rem; border-radius:999px; }
  .skip-link:focus { top:1rem; }
  header, main, footer { width:min(1120px, calc(100% - 32px)); margin:0 auto; }
  header { padding:48px 0 24px; }
  .eyebrow { color:var(--blue); text-transform:uppercase; letter-spacing:.18em; font-weight:800; font-size:.78rem; }
  h1 { max-width:980px; margin:0; font-family:Georgia,"Times New Roman",serif; font-size:clamp(2.7rem,7vw,5.7rem); line-height:.95; letter-spacing:-.05em; }
  .lede { max-width:840px; font-size:clamp(1.1rem,2.4vw,1.45rem); line-height:1.55; color:#31404a; }
  .badge { display:inline-flex; width:fit-content; padding:.45rem .75rem; border-radius:999px; background:var(--green); color:white; font-weight:900; }
  .grid { display:grid; grid-template-columns:repeat(12,1fr); gap:18px; }
  .card { grid-column:span 6; min-width:0; padding:24px; border:1px solid var(--line); border-radius:28px; background:rgba(255,250,242,.92); box-shadow:0 18px 40px rgba(35,43,50,.10); }
  .card.large { grid-column:span 12; }
  h2,h3 { font-family:Georgia,"Times New Roman",serif; letter-spacing:-.03em; }
  h2 { margin:0 0 14px; font-size:clamp(1.8rem,4vw,3rem); }
  p, li { line-height:1.65; }
  textarea, button { width:100%; border:1px solid #b9c6cc; border-radius:16px; padding:.85rem 1rem; font:inherit; }
  textarea { background:#f7f8f4; color:var(--ink); }
  button { width:fit-content; min-width:190px; border:0; background:var(--blue); color:white; font-weight:900; cursor:default; }
  .result { margin-top:18px; padding:18px; border-left:6px solid var(--green); border-radius:18px; background:white; }
  .warning { border-left-color:#b2603f; background:#fff8f4; }
  .kicker { color:var(--muted); font-size:.86rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }
  footer { padding:38px 0 56px; color:var(--muted); }
  :focus-visible { outline:4px solid var(--gold); outline-offset:3px; }
  @media (max-width:760px) { header,main,footer{margin:0;max-width:390px;width:100%;padding-left:24px;padding-right:24px}header{padding-top:34px}h1{font-size:clamp(2.2rem,11vw,3rem)}.card{grid-column:span 12;padding:20px;border-radius:22px}button{width:100%} }
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header>
  <p class="eyebrow">CivicSuite / CivicProcure public sample</p>
  <h1>Turn procurement packets into reviewable public records.</h1>
  <p class="lede">CivicProcure demonstrates procurement support: RFP outlines, proposal comparison scaffolds, exception flags, scoring summaries, staff review queues, context packets, board memo inputs, and award-packet checklists without evaluating vendors or making award decisions.</p>
  <p><span class="badge">v0.2.0 procurement support + staff review queues</span></p>
</header>
<main id="main" tabindex="-1">
  <section class="grid" aria-labelledby="lookup-title">
    <article class="card large">
      <p class="kicker">Sample RFP drafting</p>
      <h2 id="lookup-title">Bridge design RFP</h2>
      <textarea aria-label="Sample procurement notes" rows="4">Professional services procurement for bridge inspection and design support; proposals include exceptions and insurance notes.</textarea>
      <button type="button">Draft sample procurement file</button>
      <div class="result" role="status" aria-live="polite">
        <h3>Staff review packet</h3>
        <ul><li>Recommended owner: Department lead + Legal + Purchasing.</li><li>Compare responsiveness, exceptions, price factors, and review notes.</li><li>Preserve solicitation, proposal register, scoring worksheets, board memo, and award action.</li></ul>
      </div>
    </article>
    <article class="card"><p class="kicker">Comparison</p><h2>Factors, not decisions</h2><div class="result"><p>CivicProcure can scaffold proposal comparison rows and route review work to staff, but staff must perform the actual vendor evaluation.</p></div></article>
    <article class="card"><p class="kicker">Exceptions</p><h2>Flag first</h2><div class="result"><p>Exception helpers identify common indemnity, insurance, confidentiality, and deviation language for staff and legal review.</p></div></article>
    <article class="card"><p class="kicker">Award packet</p><h2>Preserve provenance</h2><div class="result"><p>Exports preserve solicitation, addenda, proposal register, evaluation worksheets, staff recommendation, board action, agreement, and retention notes.</p></div></article>
    <article class="card large"><p class="kicker">Boundary</p><h2>No official procurement action</h2><div class="result warning"><p>CivicProcure does not evaluate vendors, award contracts, make award decisions, provide legal advice, call live LLMs, use live vendor portals, submit procurements, or replace the procurement system of record.</p></div></article>
  </section>
</main>
<footer><p>CivicProcure is part of the Apache 2.0 CivicSuite open-source municipal AI project.</p></footer>
</body>
</html>
"""
