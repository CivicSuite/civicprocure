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
  button { width:fit-content; min-width:190px; border:0; background:var(--blue); color:white; font-weight:900; cursor:pointer; }
  button:disabled { opacity:.65; cursor:wait; }
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
      <label for="procurement-notes">Procurement need notes</label>
      <textarea id="procurement-notes" aria-label="Sample procurement notes" rows="4">Professional services procurement for bridge inspection and design support; proposals include exceptions and insurance notes.</textarea>
      <button id="draft-button" type="button">Draft sample procurement file</button>
      <div id="result" class="result" role="status" aria-live="polite">
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
<script>
  const result = document.querySelector("#result");
  const button = document.querySelector("#draft-button");
  const notes = document.querySelector("#procurement-notes");

  function clearResult(kind) {
    result.className = `result ${kind}`;
    result.replaceChildren();
  }

  function appendText(tagName, text) {
    const node = document.createElement(tagName);
    node.textContent = text;
    result.appendChild(node);
    return node;
  }

  function setResult(kind, title, body) {
    clearResult(kind);
    appendText("h3", title);
    appendText("p", body);
  }

  function renderDraft(payload) {
    clearResult("");
    appendText("h3", payload.heading || "Draft ready for staff review");
    const sections = Array.isArray(payload.sections) ? payload.sections : [];
    if (sections.length) {
      const list = document.createElement("ul");
      for (const section of sections) {
        const item = document.createElement("li");
        item.textContent = section;
        list.appendChild(item);
      }
      result.appendChild(list);
    }
    appendText("p", payload.disclaimer || "Staff must verify every procurement decision before official action.");
  }

  button.addEventListener("click", async () => {
    button.disabled = true;
    setResult("", "Drafting procurement file", "Sending staff-entered notes to the local CivicProcure API.");
    try {
      const cityNeed = notes.value.trim();
      if (!cityNeed) {
        setResult("warning", "More detail is needed", "Add procurement need notes before drafting a sample file.");
        return;
      }
      const response = await fetch("/api/v1/civicprocure/rfps/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          procurement_title: "Bridge design RFP",
          procurement_type: "professional services",
          city_need: cityNeed
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        const detail = payload.detail || {};
        setResult("warning", "Draft failed", detail.fix || detail.message || "Review the input and try again.");
        return;
      }
      renderDraft(payload);
    } catch {
      setResult("warning", "Draft failed", "The local CivicProcure API did not respond. Check the runtime logs and try again.");
    } finally {
      button.disabled = false;
    }
  });
</script>
</body>
</html>
"""


def render_staff_page() -> str:
    """Render the staff-facing CivicProcure review queue page."""

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CivicProcure Staff Review</title>
<style>
  :root { --ink:#1c2430; --muted:#5b6470; --paper:#f8fbf8; --blue:#244f73; --green:#2f654c; --gold:#d7aa45; --line:#cbd8ce; --warn:#9c4e32; }
  * { box-sizing:border-box; }
  body { margin:0; color:var(--ink); font-family:"Aptos","Segoe UI",sans-serif; background:#f4f8f5; }
  .skip-link { position:absolute; left:1rem; top:-4rem; background:var(--ink); color:white; padding:.7rem 1rem; border-radius:999px; }
  .skip-link:focus { top:1rem; }
  header, main, footer { width:min(1180px, calc(100% - 32px)); margin:0 auto; }
  header { padding:34px 0 18px; }
  .eyebrow { color:var(--blue); text-transform:uppercase; letter-spacing:.14em; font-weight:800; font-size:.78rem; }
  h1 { margin:.2rem 0 .6rem; font-family:Georgia,"Times New Roman",serif; font-size:clamp(2.1rem,5vw,4.6rem); line-height:1; }
  .lede { max-width:860px; color:#31404a; font-size:1.08rem; line-height:1.55; }
  .grid { display:grid; grid-template-columns:390px minmax(0,1fr); gap:18px; align-items:start; }
  .panel { min-width:0; padding:22px; border:1px solid var(--line); border-radius:8px; background:var(--paper); box-shadow:0 12px 32px rgba(35,43,50,.08); }
  h2 { margin:0 0 14px; font-size:1.35rem; }
  label { display:block; margin:.85rem 0 .35rem; font-weight:800; }
  input, textarea, button { width:100%; border:1px solid #b8c6c0; border-radius:8px; padding:.78rem .9rem; font:inherit; }
  textarea { min-height:110px; resize:vertical; }
  button { margin-top:14px; border:0; background:var(--blue); color:white; font-weight:900; cursor:pointer; }
  button.secondary { background:var(--green); }
  button:disabled { opacity:.65; cursor:wait; }
  .status { margin-top:14px; padding:14px; border-left:5px solid var(--green); background:white; border-radius:8px; line-height:1.55; }
  .warning { border-left-color:var(--warn); background:#fff8f4; }
  .review-list { display:grid; gap:12px; }
  .review { padding:14px; border:1px solid var(--line); border-radius:8px; background:white; }
  .meta { color:var(--muted); font-size:.9rem; }
  footer { padding:32px 0 48px; color:var(--muted); }
  :focus-visible { outline:4px solid var(--gold); outline-offset:3px; }
  @media (max-width:820px) { header,main,footer{width:100%;padding-left:20px;padding-right:20px}.grid{grid-template-columns:1fr}.panel{padding:18px} }
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header>
  <p class="eyebrow">CivicSuite / CivicProcure staff</p>
  <h1>Procurement review queue</h1>
  <p class="lede">Create local RFP workpapers, queue staff review, and prepare award-packet records before any publication, proposal evaluation, contract routing, or award action.</p>
</header>
<main id="main" tabindex="-1">
  <section class="grid" aria-label="CivicProcure staff workspace">
    <form id="rfp-form" class="panel">
      <h2>Create RFP workpaper</h2>
      <label for="staff-key">Staff API key</label>
      <input id="staff-key" type="password" autocomplete="off">
      <label for="procurement-title">Procurement title</label>
      <input id="procurement-title" value="Bridge design RFP">
      <label for="procurement-type">Procurement type</label>
      <input id="procurement-type" value="professional services">
      <label for="city-need">City need</label>
      <textarea id="city-need">Bridge inspection and design support with insurance and exception review.</textarea>
      <button id="create-button" type="submit">Create RFP and queue</button>
      <button id="award-button" class="secondary" type="button">Create award packet</button>
      <button id="load-button" class="secondary" type="button">Load staff queue</button>
      <div id="form-status" class="status" role="status" aria-live="polite">Ready.</div>
    </form>
    <section class="panel" aria-labelledby="queue-title">
      <h2 id="queue-title">Open procurement reviews</h2>
      <div id="queue" class="review-list" aria-live="polite"></div>
    </section>
  </section>
</main>
<footer><p>CivicProcure keeps procurement work local. Staff remain responsible for vendor evaluation, legal review, publication, awards, contracts, and system-of-record updates.</p></footer>
<script>
  const form = document.querySelector("#rfp-form");
  const keyInput = document.querySelector("#staff-key");
  const createButton = document.querySelector("#create-button");
  const awardButton = document.querySelector("#award-button");
  const loadButton = document.querySelector("#load-button");
  const statusBox = document.querySelector("#form-status");
  const queue = document.querySelector("#queue");
  let lastDraftId = "rfp-2026-local";

  function setStatus(kind, message) {
    statusBox.className = `status ${kind}`;
    statusBox.textContent = message;
  }

  function headers() {
    return {
      "Content-Type": "application/json",
      "X-CivicProcure-Role": "staff",
      "X-CivicProcure-Staff-Key": keyInput.value.trim()
    };
  }

  function field(id) {
    return document.querySelector(id).value.trim();
  }

  function renderQueue(items) {
    queue.replaceChildren();
    if (!items.length) {
      const empty = document.createElement("p");
      empty.textContent = "No staff review items yet.";
      queue.appendChild(empty);
      return;
    }
    for (const item of items) {
      const card = document.createElement("article");
      card.className = "review";
      const title = document.createElement("h3");
      title.textContent = item.procurement_title || "Untitled procurement";
      const reason = document.createElement("p");
      reason.textContent = item.reason || "Review required.";
      const meta = document.createElement("p");
      meta.className = "meta";
      meta.textContent = `${item.status || "open"} / ${item.solicitation_id || "no solicitation id"} / ${item.review_id || "no review id"}`;
      card.append(title, reason, meta);
      queue.appendChild(card);
    }
  }

  async function loadQueue() {
    setStatus("", "Loading staff queue.");
    const response = await fetch("/api/v1/civicprocure/staff/reviews", { headers: headers() });
    const payload = await response.json();
    if (!response.ok) {
      const detail = payload.detail || {};
      setStatus("warning", detail.fix || detail.message || "Queue load failed.");
      return;
    }
    renderQueue(Array.isArray(payload.items) ? payload.items : []);
    setStatus("", "Staff queue loaded.");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    createButton.disabled = true;
    setStatus("", "Creating local RFP workpaper and staff review item.");
    try {
      const response = await fetch("/api/v1/civicprocure/rfps/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          procurement_title: field("#procurement-title"),
          procurement_type: field("#procurement-type"),
          city_need: field("#city-need")
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        const detail = payload.detail || {};
        setStatus("warning", detail.fix || detail.message || "RFP draft failed.");
        return;
      }
      lastDraftId = payload.draft_id || lastDraftId;
      setStatus("", `Created RFP draft ${lastDraftId} and review ${payload.staff_review_id || "pending"}.`);
      await loadQueue();
    } catch {
      setStatus("warning", "The local CivicProcure API did not respond. Check service logs and retry.");
    } finally {
      createButton.disabled = false;
    }
  });

  awardButton.addEventListener("click", async () => {
    awardButton.disabled = true;
    setStatus("", "Creating local award packet and staff review item.");
    try {
      const response = await fetch("/api/v1/civicprocure/award-packet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ solicitation_id: lastDraftId, title: `${field("#procurement-title")} award packet` })
      });
      const payload = await response.json();
      if (!response.ok) {
        const detail = payload.detail || {};
        setStatus("warning", detail.fix || detail.message || "Award packet failed.");
        return;
      }
      setStatus("", `Created award packet ${payload.packet_id || "pending"} and review ${payload.staff_review_id || "pending"}.`);
      await loadQueue();
    } catch {
      setStatus("warning", "The local CivicProcure API did not respond. Check service logs and retry.");
    } finally {
      awardButton.disabled = false;
    }
  });

  loadButton.addEventListener("click", () => {
    loadQueue().catch(() => setStatus("warning", "The local CivicProcure API did not respond."));
  });
</script>
</body>
</html>
"""
