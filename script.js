/* Scenario-Driven Statistical Modeling — portal script.
 * Renders the paper from paper/content.json, runs the in-browser OLS vs Huber lab,
 * and drives the outline scrollspy, code tabs, and theme toggle. */
(function () {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const el = (tag, attrs = {}, text) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (text !== undefined) n.textContent = text;
    return n;
  };

  /* ---------------- Theme ---------------- */
  const THEME_KEY = "ssm-theme";
  try {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) document.documentElement.dataset.theme = saved;
  } catch (e) { /* storage unavailable */ }
  $("#themeToggle").addEventListener("click", () => {
    const dark = getComputedStyle(document.documentElement).colorScheme.includes("dark");
    const next = dark ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* ignore */ }
    drawLab();
  });

  /* ---------------- Paper rendering ---------------- */
  let nTable = 0, nFig = 0;

  function renderTable(b, results) {
    nTable += 1;
    const frag = document.createDocumentFragment();
    frag.append(el("p", { class: "tbl-label" }, `Table ${nTable}`), el("p", { class: "tbl-title" }, b.title));
    let header = b.header, rows = b.rows, numeric = false;
    if (b.source === "results") {
      numeric = true;
      header = ["Shock", "OLS RMSE", "Huber RMSE", "OLS ‖β̂−β‖", "Huber ‖β̂−β‖", "IRLS iters"];
      rows = results.rows.map((r) => [
        `${Math.round(r.contamination * 100)}%`, r.ols_rmse.toFixed(1), r.hub_rmse.toFixed(1),
        r.ols_berr.toFixed(1), r.hub_berr.toFixed(1), r.hub_iter.toFixed(1)]);
    }
    const wrap = el("div", { class: "table-wrap" });
    const t = el("table");
    const tr = el("tr");
    header.forEach((h, j) => tr.append(el("th", numeric && j ? { class: "num" } : {}, h)));
    const thead = el("thead");
    thead.append(tr);
    t.append(thead);
    const tb = el("tbody");
    rows.forEach((row) => {
      const r = el("tr");
      row.forEach((v, j) => r.append(el("td", numeric && j ? { class: "num" } : {}, v)));
      tb.append(r);
    });
    t.append(tb);
    wrap.append(t);
    frag.append(wrap, el("p", { class: "muted", style: "font-size:14px;font-style:italic" }, b.caption));
    return frag;
  }

  function renderBlock(b, results) {
    switch (b.type) {
      case "p": return el("p", {}, b.text);
      case "h3": return el("h3", {}, b.text);
      case "eq": return el("div", { class: "eq" }, `\\[ ${b.latex} \\]`);
      case "list": {
        const ul = el("ul");
        b.items.forEach((i) => ul.append(el("li", {}, i)));
        return ul;
      }
      case "table": return renderTable(b, results);
      case "figure": {
        nFig += 1;
        const f = el("figure");
        f.append(el("p", { class: "fig-label" }, `Figure ${nFig}`), el("p", { class: "fig-title" }, b.title));
        f.append(el("img", { src: b.src, alt: b.title, loading: "lazy" }), el("figcaption", { class: "muted" }, b.caption));
        return f;
      }
      default: return document.createTextNode("");
    }
  }

  function renderPaper(paper, results) {
    const a = paper.author;
    $("#course").textContent = a.course;
    $("#paperTitle").textContent = paper.title;
    $("#byline").textContent = `${a.name} · ${a.program} · ${a.school}, ${a.university}`;
    $("#status").textContent = paper.status;
    $("#abstractText").textContent = paper.abstract;
    $("#keywords").textContent = paper.keywords;

    const body = $("#paperBody");
    paper.sections.forEach((s) => {
      const sec = el("section", { id: s.id, class: "paper-section" });
      sec.append(el("h2", {}, `${s.number}. ${s.title}`));
      s.blocks.forEach((b) => sec.append(renderBlock(b, results)));
      body.append(sec);
    });
    const refs = el("section", { id: "references", class: "paper-section" });
    refs.append(el("h2", {}, `${paper.sections.length + 1}. References`));
    const ol = el("ul", { class: "refs" });
    [...paper.references].sort().forEach((r) => ol.append(el("li", {}, r)));
    refs.append(ol);
    body.append(refs);

    const bp = paper.appendix.find((x) => x.text);
    if (bp) $("#blueprint").textContent = bp.text;

    // Outline: abstract, lab, numbered sections, references, code.
    const toc = $("#tocList");
    const items = [["abstract", "Abstract"], ["lab", "Interactive Lab"]]
      .concat(paper.sections.map((s) => [s.id, `${s.number}. ${s.title}`]))
      .concat([["references", `${paper.sections.length + 1}. References`], ["code", `${paper.sections.length + 2}. Appendix & Code`]]);
    items.forEach(([id, label]) => {
      const li = el("li");
      li.append(el("a", { href: `#${id}` }, label));
      toc.append(li);
    });
    scrollSpy();
    typeset();
  }

  function typeset() {
    if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise();
    else window.addEventListener("load", () => window.MathJax && MathJax.typesetPromise && MathJax.typesetPromise());
  }

  function scrollSpy() {
    const links = [...document.querySelectorAll(".toc a")];
    const byId = new Map(links.map((a) => [a.getAttribute("href").slice(1), a]));
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        links.forEach((a) => a.classList.remove("active"));
        const a = byId.get(e.target.id);
        if (a) a.classList.add("active");
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    byId.forEach((_, id) => { const s = document.getElementById(id); if (s) obs.observe(s); });
  }

  function loadFailed(err) {
    $("#paperBody").append(el("p", { class: "socratic" },
      `Could not load paper content (${err.message}). Serve the folder over HTTP, e.g. "python3 -m http.server", instead of opening the file directly.`));
  }

  Promise.all([
    fetch("paper/content.json").then((r) => r.json()),
    fetch("results/results.json").then((r) => r.json()),
  ]).then(([p, r]) => renderPaper(p, r)).catch(loadFailed);

  /* ---------------- Lab: OLS vs Huber in the browser ---------------- */
  // Mirrors model/baseline.py and model/revised.py for one feature: y = b0 + b1 x.
  const TRUE = { b0: 300, b1: 85, sd: 40 };
  const N_TRAIN = 150, N_TEST = 600;
  let seed = 623;

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function normalSampler(rand) {
    return () => {
      const u = Math.max(rand(), 1e-12), v = rand();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);   // Box–Muller
    };
  }
  function makeData(n, randn) {
    const x = new Float64Array(n), y = new Float64Array(n);
    for (let i = 0; i < n; i++) { x[i] = randn(); y[i] = TRUE.b0 + TRUE.b1 * x[i] + TRUE.sd * randn(); }
    return { x, y };
  }
  function shuffledIndex(n, rand) {
    const idx = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; }
    return idx;
  }

  // Weighted least squares for one feature; w = 1 gives OLS.
  function wls(x, y, w) {
    let sw = 0, sx = 0, sy = 0;
    for (let i = 0; i < x.length; i++) { sw += w[i]; sx += w[i] * x[i]; sy += w[i] * y[i]; }
    const mx = sx / sw, my = sy / sw;
    let sxy = 0, sxx = 0;
    for (let i = 0; i < x.length; i++) { const dx = x[i] - mx; sxy += w[i] * dx * (y[i] - my); sxx += w[i] * dx * dx; }
    const b1 = sxy / Math.max(sxx, 1e-12);
    return { b0: my - b1 * mx, b1 };
  }
  function median(a) {
    const s = Float64Array.from(a).sort(), m = s.length >> 1;
    return s.length % 2 ? s[m] : 0.5 * (s[m - 1] + s[m]);
  }
  function huber(x, y, delta, maxIter = 100, tol = 1e-8) {
    const n = x.length;
    let beta = wls(x, y, new Float64Array(n).fill(1));
    const w = new Float64Array(n), r = new Float64Array(n);
    let it = 0, s = 1;
    for (it = 1; it <= maxIter; it++) {
      for (let i = 0; i < n; i++) r[i] = y[i] - beta.b0 - beta.b1 * x[i];
      const med = median(r);
      s = Math.max(1.4826 * median(r.map((v) => Math.abs(v - med))), 1e-12);
      for (let i = 0; i < n; i++) w[i] = Math.min(1, delta / Math.max(Math.abs(r[i] / s), 1e-12));
      const nb = wls(x, y, w);
      const step = Math.hypot(nb.b0 - beta.b0, nb.b1 - beta.b1);
      beta = nb;
      if (step <= tol * (1 + Math.hypot(beta.b0, beta.b1))) break;
    }
    return { ...beta, w, iters: Math.min(it, maxIter), s };
  }
  function rmse(beta, d) {
    let acc = 0;
    for (let i = 0; i < d.x.length; i++) { const e = d.y[i] - beta.b0 - beta.b1 * d.x[i]; acc += e * e; }
    return Math.sqrt(acc / d.x.length);
  }

  let labData = null;
  function sampleLab() {
    const rand = mulberry32(seed), randn = normalSampler(rand);
    labData = { train: makeData(N_TRAIN, randn), test: makeData(N_TEST, randn), order: shuffledIndex(N_TRAIN, rand) };
  }

  const SVG_NS = "http://www.w3.org/2000/svg";
  const svgEl = (tag, attrs) => {
    const n = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    return n;
  };
  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  function drawLab() {
    if (!labData) return;
    const c = +$("#cIn").value / 100, factor = +$("#fIn").value, delta = +$("#dIn").value;
    $("#cOut").textContent = `${Math.round(c * 100)}%`;
    $("#fOut").textContent = `×${factor}`;
    $("#dOut").textContent = delta.toFixed(3);

    const { train, test, order } = labData;
    const y = Float64Array.from(train.y), shocked = new Uint8Array(N_TRAIN);
    const k = Math.round(c * N_TRAIN);
    for (let j = 0; j < k; j++) { y[order[j]] *= factor; shocked[order[j]] = 1; }
    const ols = wls(train.x, y, new Float64Array(N_TRAIN).fill(1));
    const hub = huber(train.x, y, delta);

    // Chart geometry.
    const W = 640, H = 380, m = { l: 56, r: 64, t: 12, b: 42 };
    const X0 = -3.2, X1 = 3.2, Y0 = -100, Y1 = 1100;
    const sx = (v) => m.l + ((v - X0) / (X1 - X0)) * (W - m.l - m.r);
    const sy = (v) => m.t + (1 - (v - Y0) / (Y1 - Y0)) * (H - m.t - m.b);
    const svg = $("#chart");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.replaceChildren();
    const grid = cssVar("--border"), dim = cssVar("--fg-dim"), fg = cssVar("--fg"), bg = cssVar("--bg");

    const defs = svgEl("defs", {});
    const clip = svgEl("clipPath", { id: "plotClip" });
    clip.append(svgEl("rect", { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b }));
    defs.append(clip);
    svg.append(defs);

    for (let v = 0; v <= 1000; v += 250) {
      svg.append(svgEl("line", { x1: m.l, x2: W - m.r, y1: sy(v), y2: sy(v), stroke: grid, "stroke-width": 1 }));
      const t = svgEl("text", { x: m.l - 8, y: sy(v) + 4, "text-anchor": "end", "font-size": 11, fill: dim });
      t.textContent = v; svg.append(t);
    }
    for (let v = -3; v <= 3; v++) {
      const t = svgEl("text", { x: sx(v), y: H - m.b + 18, "text-anchor": "middle", "font-size": 11, fill: dim });
      t.textContent = v; svg.append(t);
    }
    const xl = svgEl("text", { x: (m.l + W - m.r) / 2, y: H - 6, "text-anchor": "middle", "font-size": 12, fill: dim });
    xl.textContent = "House size (standardized)"; svg.append(xl);
    const yl = svgEl("text", { x: 14, y: (m.t + H - m.b) / 2, "text-anchor": "middle", "font-size": 12, fill: dim, transform: `rotate(-90 14 ${(m.t + H - m.b) / 2})` });
    yl.textContent = "Price ($1000s)"; svg.append(yl);

    // Points: clean rows filled, shocked rows hollow; opacity encodes Huber weight.
    const pts = svgEl("g", {});
    for (let i = 0; i < N_TRAIN; i++) {
      const cy = Math.min(Math.max(sy(y[i]), m.t + 4), H - m.b - 4);
      const op = (0.25 + 0.75 * hub.w[i]).toFixed(2);
      const p = shocked[i]
        ? svgEl("circle", { cx: sx(train.x[i]), cy, r: 4.5, fill: "none", stroke: fg, "stroke-width": 1.4, opacity: op })
        : svgEl("circle", { cx: sx(train.x[i]), cy, r: 3.5, fill: cssVar("--pt"), stroke: bg, "stroke-width": 1, opacity: op });
      p.dataset.i = i;
      pts.append(p);
    }
    svg.append(pts);

    // Fitted lines with direct labels.
    const lines = svgEl("g", { "clip-path": "url(#plotClip)" });
    [[ols, "--ols"], [hub, "--hub"]].forEach(([b, col]) => {
      lines.append(svgEl("line", { x1: sx(X0), y1: sy(b.b0 + b.b1 * X0), x2: sx(X1), y2: sy(b.b0 + b.b1 * X1), stroke: cssVar(col), "stroke-width": 2.5, "stroke-linecap": "round" }));
    });
    svg.append(lines);
    const yo = ols.b0 + ols.b1 * X1, yh = hub.b0 + hub.b1 * X1;
    let lo = sy(yo), lh = sy(yh);
    if (Math.abs(lo - lh) < 14) { const mid = (lo + lh) / 2; lo = mid - 8 * Math.sign(lh - lo || 1); lh = mid + 8 * Math.sign(lh - lo || 1); }
    [["OLS", lo], ["Huber", lh]].forEach(([name, yy]) => {
      const t = svgEl("text", { x: W - m.r + 6, y: Math.min(Math.max(yy, m.t + 10), H - m.b) + 4, "font-size": 12, fill: fg });
      t.textContent = name; svg.append(t);
    });

    // Tooltip on hover.
    const tip = $("#tip"), wrap = svg.parentElement;
    pts.querySelectorAll("circle").forEach((p) => {
      p.style.cursor = "default";
      p.addEventListener("pointerenter", () => {
        const i = +p.dataset.i;
        tip.innerHTML = `<b>${shocked[i] ? "Shocked row" : "Clean row"}</b><br>size ${train.x[i].toFixed(2)} · price ${y[i].toFixed(0)}<br>Huber weight w = ${hub.w[i].toFixed(2)}`;
        tip.hidden = false;
        const box = svg.getBoundingClientRect(), wb = wrap.getBoundingClientRect(), scale = box.width / W;
        const left = box.left - wb.left + (+p.getAttribute("cx")) * scale + 10;
        tip.style.left = `${Math.min(left, wb.width - 190)}px`;
        tip.style.top = `${box.top - wb.top + (+p.getAttribute("cy")) * scale - 10}px`;
      });
      p.addEventListener("pointerleave", () => { tip.hidden = true; });
    });

    // Metrics.
    const card = (label, col, value, sub) =>
      `<div class="metric"><div class="label">${col ? `<i class="sw ${col}"></i>` : ""}${label}</div><div class="value">${value}</div><div class="sub">${sub}</div></div>`;
    $("#metrics").innerHTML =
      card("OLS clean-test RMSE", "ols", rmse(ols, test).toFixed(1), `β̂₁ = ${ols.b1.toFixed(1)} (true 85)`) +
      card("Huber clean-test RMSE", "hub", rmse(hub, test).toFixed(1), `β̂₁ = ${hub.b1.toFixed(1)} · ${hub.iters} IRLS iters`) +
      card("Noise floor σ", "", TRUE.sd.toFixed(1), "best achievable RMSE") +
      card("Rows down-weighted", "", `${Array.from(hub.w).filter((v) => v < 1).length}`, `of ${N_TRAIN} (w < 1); ${k} shocked`);
  }

  ["#cIn", "#fIn", "#dIn"].forEach((s) => $(s).addEventListener("input", drawLab));
  $("#reseed").addEventListener("click", () => { seed = (seed * 1103515245 + 12345) >>> 0; sampleLab(); drawLab(); });
  if (window.matchMedia) matchMedia("(prefers-color-scheme: dark)").addEventListener("change", drawLab);
  sampleLab();
  drawLab();

  /* ---------------- Code tabs ---------------- */
  const KW = /\b(def|return|import|from|as|for|in|if|else|elif|with|not|and|or|None|True|False|break|class|while|lambda)\b/g;
  function highlight(src) {
    const esc = src.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    // Tokenize comments and strings first so keyword coloring never touches them.
    return esc.replace(/("""[\s\S]*?"""|"[^"\n]*"|'[^'\n]*'|#[^\n]*)|(\b\d+(?:\.\d+)?(?:e-?\d+)?\b)|([A-Za-z_]+)/g, (m, strOrCom, num, word) => {
      if (strOrCom) return `<span class="${strOrCom.startsWith("#") ? "tok-c" : "tok-s"}">${strOrCom}</span>`;
      if (num) return `<span class="tok-n">${num}</span>`;
      KW.lastIndex = 0;
      return KW.test(word) ? `<span class="tok-k">${word}</span>` : word;
    });
  }
  const codeCache = {};
  function showCode(file) {
    const view = $("#codeView");
    const render = (src) => { view.innerHTML = highlight(src); };
    if (codeCache[file]) return render(codeCache[file]);
    view.textContent = "Loading…";
    fetch(file).then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); })
      .then((t) => { codeCache[file] = t; render(t); })
      .catch(() => { view.textContent = `Could not load ${file}. Serve the site over HTTP to view source.`; });
  }
  document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => { x.classList.toggle("active", x === t); x.setAttribute("aria-selected", x === t); });
    showCode(t.dataset.file);
  }));
  showCode("model/baseline.py");
})();
