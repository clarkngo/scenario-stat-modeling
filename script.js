/* Forecasting Market Risk from Scratch — portal script.
 * Renders the paper from paper/content.json, runs the in-browser Value-at-Risk lab on the
 * real daily returns, and drives the outline scrollspy, code tabs, and theme toggle. */
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

  function renderTable(b) {
    nTable += 1;
    const frag = document.createDocumentFragment();
    frag.append(el("p", { class: "tbl-label" }, `Table ${nTable}`), el("p", { class: "tbl-title" }, b.title));
    const numeric = !!b.numeric;   // right-align every column after the first
    const wrap = el("div", { class: "table-wrap" });
    const t = el("table");
    const tr = el("tr");
    b.header.forEach((h, j) => tr.append(el("th", numeric && j ? { class: "num" } : {}, h)));
    const thead = el("thead");
    thead.append(tr);
    t.append(thead);
    const tb = el("tbody");
    b.rows.forEach((row) => {
      const r = el("tr");
      row.forEach((v, j) => r.append(el("td", numeric && j ? { class: "num" } : {}, v)));
      tb.append(r);
    });
    t.append(tb);
    wrap.append(t);
    frag.append(wrap, el("p", { class: "muted", style: "font-size:14px;font-style:italic" }, b.caption));
    return frag;
  }

  function renderBlock(b) {
    switch (b.type) {
      case "p": return el("p", {}, b.text);
      case "h3": return el("h3", {}, b.text);
      case "eq": return el("div", { class: "eq" }, `\\[ ${b.latex} \\]`);
      case "list": {
        const ul = el("ul");
        b.items.forEach((i) => ul.append(el("li", {}, i)));
        return ul;
      }
      case "table": return renderTable(b);
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

  function renderPaper(paper) {
    const a = paper.affiliation;
    const names = paper.authors.map((x) => x.name).join(" & ");
    $("#course").textContent = a.course;
    $("#paperTitle").textContent = paper.title;
    $("#byline").textContent = `${names} · ${a.program} · ${a.school}, ${a.university}`;
    $("#status").textContent = paper.status;
    $("#abstractText").textContent = paper.abstract;
    $("#keywords").textContent = paper.keywords;

    const body = $("#paperBody");
    paper.sections.forEach((s) => {
      const sec = el("section", { id: s.id, class: "paper-section" });
      sec.append(el("h2", {}, `${s.number}. ${s.title}`));
      s.blocks.forEach((b) => sec.append(renderBlock(b)));
      body.append(sec);
    });
    const refs = el("section", { id: "references", class: "paper-section" });
    refs.append(el("h2", {}, `${paper.sections.length + 1}. References`));
    const ol = el("ul", { class: "refs" });
    // References mark italic spans (APA titles) with *asterisks*.
    paper.references.map((r) => r.text).sort((x, y) => x.toLowerCase().localeCompare(y.toLowerCase())).forEach((r) => {
      const li = el("li");
      r.split("*").forEach((chunk, k) => li.append(k % 2 ? el("i", {}, chunk) : document.createTextNode(chunk)));
      ol.append(li);
    });
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

  fetch("paper/content.json").then((r) => r.json()).then(renderPaper).catch(loadFailed);

  /* ---------------- Lab: Value-at-Risk replay on real data ---------------- */
  // Mirrors model/garch.py: the same variance recursion, started in 1990 with the
  // parameters and quantiles that model/run_garch.py fitted on 1990–2014.
  const PERIODS = {
    covid: [20200101, 20200701, "January–June 2020"],
    y2022: [20220101, 20230101, "2022"],
    y2025: [20250201, 20250701, "February–June 2025"],
    test: [20150101, 20270101, "The full test period, 2015–2026"],
    gfc: [20080701, 20090701, "July 2008–June 2009 (inside the training data)"],
  };
  const LAB_MODELS = [
    { key: "rolling", label: "Past-year rule", color: "--pt" },
    { key: "garch-n", label: "GARCH, normal", color: "--ols" },
    { key: "gjr-t", label: "GJR-GARCH-t", color: "--hub" },
  ];
  const lab = { period: "covid", level: "0.01", dates: null, r: null, sigma: {}, models: null };

  function garchSigma(p, r) {
    const out = new Float64Array(r.length);
    let s2 = p.s2_0;
    out[0] = Math.sqrt(s2);
    for (let t = 1; t < r.length; t++) {
      const e = r[t - 1] - p.mu;
      s2 = p.omega + (p.alpha + (e < 0 ? p.gamma : 0)) * e * e + p.beta * s2;
      out[t] = Math.sqrt(s2);
    }
    return out;
  }
  function rollingSigma(r, w = 250) {
    const out = new Float64Array(r.length).fill(NaN);
    let s = 0, s2 = 0;
    for (let t = 0; t < r.length; t++) {
      if (t >= w) { const m = s / w; out[t] = Math.sqrt(Math.max(s2 / w - m * m, 0)); }
      s += r[t]; s2 += r[t] * r[t];
      if (t >= w) { s -= r[t - w]; s2 -= r[t - w] * r[t - w]; }
    }
    return out;
  }

  const SVG_NS = "http://www.w3.org/2000/svg";
  const svgEl = (tag, attrs) => {
    const n = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    return n;
  };
  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const fmtDate = (d) => `${String(d).slice(0, 4)}-${String(d).slice(4, 6)}-${String(d).slice(6)}`;
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  function drawLab() {
    if (!lab.dates) return;
    const [d0, d1, periodName] = PERIODS[lab.period];
    let i0 = lab.dates.findIndex((d) => d >= d0), i1 = lab.dates.findIndex((d) => d >= d1);
    if (i1 < 0) i1 = lab.dates.length;
    const n = i1 - i0, lv = +lab.level;
    const series = LAB_MODELS.map((m) => {
      const p = lab.models[m.key];
      const mu = p.params ? p.params.mu : lab.models["garch-n"].params.mu;
      const q = p.quantiles[lab.level], sig = lab.sigma[m.key];
      const v = new Float64Array(n), hit = new Uint8Array(n);
      for (let k = 0; k < n; k++) { v[k] = mu + q * sig[i0 + k]; hit[k] = lab.r[i0 + k] < v[k] ? 1 : 0; }
      return { ...m, v, hit };
    });

    // Chart geometry.
    const W = 720, H = 380, mg = { l: 48, r: 14, t: 12, b: 70 };
    let lo = 0, hi = 0;
    for (let k = 0; k < n; k++) {
      lo = Math.min(lo, lab.r[i0 + k]); hi = Math.max(hi, lab.r[i0 + k]);
      series.forEach((s) => { lo = Math.min(lo, s.v[k]); });
    }
    const step = hi - lo > 12 ? 5 : hi - lo > 6 ? 2 : 1;
    lo = Math.floor(lo / step) * step; hi = Math.ceil(hi / step) * step;
    const plotB = H - mg.b;
    const sx = (k) => mg.l + (k + 0.5) / n * (W - mg.l - mg.r);
    const sy = (v) => mg.t + (1 - (v - lo) / (hi - lo)) * (plotB - mg.t);
    const svg = $("#chart");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.replaceChildren();
    const grid = cssVar("--border"), dim = cssVar("--fg-dim"), fg = cssVar("--fg");

    for (let v = lo; v <= hi + 1e-9; v += step) {
      svg.append(svgEl("line", { x1: mg.l, x2: W - mg.r, y1: sy(v), y2: sy(v), stroke: v === 0 ? dim : grid, "stroke-width": 1 }));
      const t = svgEl("text", { x: mg.l - 8, y: sy(v) + 4, "text-anchor": "end", "font-size": 11, fill: dim });
      t.textContent = `${v}%`; svg.append(t);
    }
    // Month (or year) ticks.
    const longSpan = n > 400;
    let lastLabel = "";
    for (let k = 0; k < n; k++) {
      const d = lab.dates[i0 + k], y = Math.floor(d / 10000), m = Math.floor(d / 100) % 100;
      const label = longSpan ? String(y) : `${MONTHS[m - 1]}${m === 1 || k === 0 ? " " + y : ""}`;
      const key = longSpan ? String(y) : `${y}-${m}`;
      if (key !== lastLabel) {
        lastLabel = key;
        if (longSpan && m > 1 && k > 0) continue;
        const t = svgEl("text", { x: sx(k), y: plotB + 16, "text-anchor": "start", "font-size": 11, fill: dim });
        t.textContent = label; svg.append(t);
      }
    }
    // Returns as thin bars.
    const bars = svgEl("g", { stroke: cssVar("--ret"), "stroke-width": Math.max(0.6, Math.min(2.5, (W - mg.l - mg.r) / n * 0.6)) });
    for (let k = 0; k < n; k++) bars.append(svgEl("line", { x1: sx(k), x2: sx(k), y1: sy(0), y2: sy(lab.r[i0 + k]) }));
    svg.append(bars);
    // VaR lines.
    series.forEach((s) => {
      let dpath = "";
      for (let k = 0; k < n; k++) dpath += `${k ? "L" : "M"}${sx(k).toFixed(1)},${sy(s.v[k]).toFixed(1)}`;
      svg.append(svgEl("path", { d: dpath, fill: "none", stroke: cssVar(s.color), "stroke-width": 2, "stroke-linejoin": "round" }));
    });
    // Breach ticks: one row per model below the axis labels.
    series.forEach((s, m) => {
      const y = plotB + 28 + m * 12;
      const lab0 = svgEl("text", { x: mg.l - 8, y: y + 4, "text-anchor": "end", "font-size": 9, fill: dim });
      lab0.textContent = ["Naive", "Orig.", "Rev."][m]; svg.append(lab0);
      svg.append(svgEl("line", { x1: mg.l, x2: W - mg.r, y1: y, y2: y, stroke: grid, "stroke-width": 1 }));
      for (let k = 0; k < n; k++) if (s.hit[k]) svg.append(svgEl("line", { x1: sx(k), x2: sx(k), y1: y - 5, y2: y + 5, stroke: cssVar(s.color), "stroke-width": 2.5 }));
    });

    // Hover readout.
    const tip = $("#tip"), wrap = svg.parentElement;
    const overlay = svgEl("rect", { x: mg.l, y: mg.t, width: W - mg.l - mg.r, height: plotB - mg.t, fill: "transparent" });
    const cursor = svgEl("line", { y1: mg.t, y2: plotB, stroke: fg, "stroke-width": 1, "stroke-dasharray": "3 3", visibility: "hidden" });
    svg.append(cursor, overlay);
    overlay.addEventListener("pointermove", (ev) => {
      const box = svg.getBoundingClientRect(), scale = box.width / W;
      const k = Math.max(0, Math.min(n - 1, Math.round(((ev.clientX - box.left) / scale - mg.l) / (W - mg.l - mg.r) * n - 0.5)));
      cursor.setAttribute("x1", sx(k)); cursor.setAttribute("x2", sx(k)); cursor.setAttribute("visibility", "visible");
      const rr = lab.r[i0 + k];
      tip.innerHTML = `<b>${fmtDate(lab.dates[i0 + k])}</b> · return ${rr.toFixed(2)}%<br>` +
        series.map((s) => `${s.label}: ${s.v[k].toFixed(2)}%${s.hit[k] ? " <b>breached</b>" : ""}`).join("<br>");
      tip.hidden = false;
      const wb = wrap.getBoundingClientRect(), x = box.left - wb.left + sx(k) * scale;
      tip.style.left = `${x > wb.width / 2 ? x - 230 : x + 12}px`;
      tip.style.top = `${box.top - wb.top + 20}px`;
    });
    overlay.addEventListener("pointerleave", () => { tip.hidden = true; cursor.setAttribute("visibility", "hidden"); });

    // Metrics.
    const expected = lv * n;
    const swatch = { rolling: "naive", "garch-n": "ols", "gjr-t": "hub" };
    $("#metrics").innerHTML = series.map((s) => {
      const k = s.hit.reduce((a, b) => a + b, 0);
      let avg = 0; for (let t = 0; t < n; t++) avg += s.v[t];
      return `<div class="metric"><div class="label"><i class="sw ${swatch[s.key]}"></i>${s.label}</div>` +
        `<div class="value">${k} <span class="unit">breaches</span></div>` +
        `<div class="sub">${(k / n * 100).toFixed(1)}% of days · avg limit ${(avg / n).toFixed(2)}%</div></div>`;
    }).join("") +
      `<div class="metric"><div class="label">A perfect ${Math.round(lv * 100)}% model</div><div class="value">≈${expected < 10 ? expected.toFixed(1) : Math.round(expected)}</div>` +
      `<div class="sub">expected breaches in ${n} trading days</div></div>`;
    $("#labCaption").textContent = `${periodName}: ${n} trading days. Ticks under the chart mark days whose loss broke each model's ${Math.round(lv * 100)}% limit.` +
      (lab.period === "gfc" ? " These days were part of the fitting data, so this is not an out-of-sample test." : "");
  }

  function initLab(csv, res) {
    const rows = csv.trim().split("\n").slice(1).map((l) => l.split(","));
    const keep = rows.filter((c) => +c[0] >= res.meta.start);
    lab.dates = keep.map((c) => +c[0]);
    lab.r = Float64Array.from(keep, (c) => +c[1] + +c[2]);   // total market return, %
    lab.models = res.models;
    lab.sigma.rolling = rollingSigma(lab.r);
    ["garch-n", "gjr-t"].forEach((k) => { lab.sigma[k] = garchSigma(res.models[k].params, lab.r); });
    drawLab();
  }
  function chipGroup(attr, setter) {
    document.querySelectorAll(`.chip[data-${attr}]`).forEach((b) => b.addEventListener("click", () => {
      document.querySelectorAll(`.chip[data-${attr}]`).forEach((x) => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
      setter(b.dataset[attr]);
      drawLab();
    }));
  }
  chipGroup("period", (v) => { lab.period = v; });
  chipGroup("level", (v) => { lab.level = v; });
  if (window.matchMedia) matchMedia("(prefers-color-scheme: dark)").addEventListener("change", drawLab);
  Promise.all([
    fetch("data/french_daily.csv").then((r) => r.text()),
    fetch("results/garch_results.json").then((r) => r.json()),
  ]).then(([csv, res]) => initLab(csv, res)).catch(() => {
    $("#metrics").innerHTML = `<div class="metric"><div class="sub">Could not load the data. Serve the folder over HTTP (python3 -m http.server).</div></div>`;
  });

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
  showCode("model/garch.py");
})();
