#!/usr/bin/env node
/* =============================================================================
   Carousel renderer — manifest.json -> 4:5 PNG slides + caption + contact sheet.

   Render path: HTML/CSS design system (template.html) -> headless Chromium
   screenshot of a 1080x1350 viewport at deviceScaleFactor=scale. Fonts are
   embedded as base64 data-URIs so output is identical on any machine.

   Usage:
     node render.js <manifest.json>              # render PNGs + caption + sheet
     node render.js <manifest.json> --preview    # write+open preview.html only
     node render.js <manifest.json> --scale 1    # 1080x1350 (default 2 = 2160x2700)
     node render.js <manifest.json> --out DIR     # override output dir (default: the manifest's dir)
     node render.js <manifest.json> --no-open     # don't open the result
============================================================================= */
const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");
const { execFile } = require("child_process");

const SCRIPT_DIR = __dirname;
const FONT_DIR = path.join(SCRIPT_DIR, "..", "assets", "fonts");
const TEMPLATE = path.join(SCRIPT_DIR, "template.html");
const W = 1080, H = 1350;

// font file -> {family, weight range}. Variable fonts get a 100-900 range.
const FONT_MAP = [
  ["SpaceGrotesk.ttf",       "Space Grotesk",       "100 900"],
  ["BricolageGrotesque.ttf", "Bricolage Grotesque", "100 900"],
  ["HankenGrotesk.ttf",      "Hanken Grotesk",      "100 900"],
  ["Fraunces.ttf",           "Fraunces",            "100 900"],
  ["Anton.ttf",              "Anton",               "400"],
];

function parseArgs(argv) {
  const a = { _: [], scale: 2, open: true, preview: false };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--preview") a.preview = true;
    else if (t === "--no-open") a.open = false;
    else if (t === "--scale") a.scale = parseFloat(argv[++i]);
    else if (t === "--out") a.out = argv[++i];
    else a._.push(t);
  }
  return a;
}

function fontFaceCss() {
  return FONT_MAP.map(([file, family, weight]) => {
    const p = path.join(FONT_DIR, file);
    if (!fs.existsSync(p)) { console.warn(`[carousel] missing font ${file}`); return ""; }
    const b64 = fs.readFileSync(p).toString("base64");
    return `@font-face{font-family:'${family}';src:url(data:font/ttf;base64,${b64}) format('truetype');`
         + `font-weight:${weight};font-style:normal;font-display:block;}`;
  }).join("\n");
}

// ---- image embedding: slide `image` fields (cover_image, media) become
// base64 data-URIs so the deck stays self-contained — same trick as the fonts.
const MIME = { ".png":"image/png", ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".webp":"image/webp", ".gif":"image/gif" };
// strip any ?query/#fragment BEFORE extname, else a dotted query (?v=1.2.3) fools it
const mimeFromExt = p => MIME[path.extname(String(p).split(/[?#]/)[0]).toLowerCase()] || "image/png";

function fetchBuffer(url, depth = 0) {
  return new Promise((resolve, reject) => {
    if (depth > 5) return reject(new Error("too many redirects"));
    const mod = url.startsWith("https") ? https : http;
    const req = mod.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        return resolve(fetchBuffer(new URL(res.headers.location, url).toString(), depth + 1));
      }
      if (res.statusCode !== 200) { res.resume(); return reject(new Error(`HTTP ${res.statusCode}`)); }
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => resolve({ buf: Buffer.concat(chunks), contentType: res.headers["content-type"] || "" }));
    });
    req.on("error", reject);
    // a half-open connection (CDN accepts TCP, never responds) would hang the whole render forever
    req.setTimeout(15000, () => req.destroy(new Error(`timeout ${url}`)));
  });
}

async function toDataUri(src, baseDir) {
  try {
    if (src.startsWith("data:")) return src;
    if (/^https?:\/\//i.test(src)) {
      const { buf, contentType } = await fetchBuffer(src);
      const mime = (contentType.split(";")[0].trim()) || mimeFromExt(src);
      return `data:${mime};base64,${buf.toString("base64")}`;
    }
    const p = path.isAbsolute(src) ? src : path.resolve(baseDir, src);
    if (!fs.existsSync(p)) { console.warn(`[carousel] missing image ${src}`); return ""; }
    return `data:${mimeFromExt(p)};base64,${fs.readFileSync(p).toString("base64")}`;
  } catch (e) { console.warn(`[carousel] image failed ${src}: ${e.message}`); return ""; }
}

async function embedImages(manifest, baseDir) {
  for (const s of manifest.slides || []) {
    if (!s) continue;
    if (typeof s.image === "string" && s.image) s.image = await toDataUri(s.image, baseDir);
    else if (s.image != null) s.image = "";   // ignore non-string image values
    // a cover_image with no usable image degrades to a clean typographic cover
    if (s.type === "cover_image" && !s.image) s.type = "cover";
  }
}

function buildHtml(manifest, { bakeManifest }) {
  let html = fs.readFileSync(TEMPLATE, "utf8");
  html = html.replace("<!--FONTFACE-->", `<style>\n${fontFaceCss()}\n</style>`);
  // preview.html bakes the manifest so opening the file auto-renders;
  // the Playwright path injects it explicitly via evaluate() instead.
  html = html.replace("<!--MANIFEST-->", bakeManifest
    ? `window.MANIFEST=${JSON.stringify(manifest)};`
    : "");
  return html;
}

function openFile(p) {
  // default-browser opener by platform: macOS `open`, Linux `xdg-open`, Windows `cmd /c start`
  const onErr = (e) => { if (e) console.warn("[carousel] could not auto-open:", e.message); };
  if (process.platform === "darwin") execFile("open", [p], onErr);
  else if (process.platform === "win32") execFile("cmd", ["/c", "start", "", p], onErr);
  else execFile("xdg-open", [p], onErr);
}

function writeCaption(manifest, outDir) {
  const c = manifest.caption || {};
  const tags = Array.isArray(c.hashtags) ? c.hashtags.join(" ") : (c.hashtags || "");
  const parts = [];
  if (c.hook) parts.push(c.hook);
  if (c.body) parts.push(c.body);
  if (c.cta) parts.push(c.cta);
  const caption = parts.join("\n\n");
  const md = `# Caption — ${manifest.topic || manifest.slug}\n\n`
    + "## Instagram caption\n\n```\n" + caption + (tags ? "\n\n" + tags : "") + "\n```\n"
    + (c.first_comment ? "\n## First comment\n\n```\n" + c.first_comment + "\n```\n" : "")
    + `\n_${(caption + (tags ? " " + tags : "")).length} chars (caption+tags)._\n`;
  fs.writeFileSync(path.join(outDir, "caption.md"), md);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const manifestPath = args._[0];
  if (!manifestPath) { console.error("usage: node render.js <manifest.json> [--preview] [--scale N] [--out DIR]"); process.exit(1); }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const manifestDir = path.dirname(path.resolve(manifestPath));
  // slides land beside the manifest (carousel/outputs/<slug>/carousel.json by
  // convention) so the deck, its cover/ variants and the PNGs stay together
  // regardless of cwd; --out DIR overrides.
  const outDir = args.out ? path.resolve(args.out) : manifestDir;
  fs.mkdirSync(outDir, { recursive: true });
  const nSlides = (manifest.slides || []).length;
  if (!nSlides) { console.error("[carousel] manifest has no slides"); process.exit(1); }

  // inline any slide images as base64 so preview.html + the render are self-contained.
  // paths resolve relative to the manifest file's dir (where cover.py drops cover/).
  await embedImages(manifest, manifestDir);

  // ---- preview mode: write a standalone HTML and open it, no browser render
  if (args.preview) {
    const html = buildHtml(manifest, { bakeManifest: true });
    const p = path.join(outDir, "preview.html");
    fs.writeFileSync(p, html);
    console.log(`[carousel] preview -> ${p}`);
    if (args.open) openFile(p);
    return;
  }

  // ---- full render via Playwright
  const { chromium } = require("playwright");
  const html = buildHtml(manifest, { bakeManifest: false });
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: W, height: H },
    deviceScaleFactor: args.scale,
  });
  await page.setContent(html, { waitUntil: "load" });
  // render with fonts loaded + text auto-fit
  await page.evaluate(async (m) => { await document.fonts.ready; window.renderDeck(m); }, manifest);
  await page.waitForTimeout(120);

  const files = [];
  for (let i = 0; i < nSlides; i++) {
    // isolate slide i at 0,0 so a clip screenshot is pixel-exact
    await page.evaluate((idx) => {
      const deck = document.getElementById("deck");
      deck.style.cssText = "padding:0;gap:0;display:block";
      document.querySelectorAll(".slide").forEach((s, j) => { s.style.display = j === idx ? "flex" : "none"; });
      window.scrollTo(0, 0);
    }, i);
    const file = path.join(outDir, `slide_${String(i + 1).padStart(2, "0")}.png`);
    await page.screenshot({ path: file, clip: { x: 0, y: 0, width: W, height: H } });
    files.push(file);
  }
  console.log(`[carousel] rendered ${files.length} slides @ ${W * args.scale}x${H * args.scale} -> ${outDir}`);

  // ---- contact sheet (all slides in one grid for quick review)
  const cols = Math.min(nSlides, 4);
  const cell = 360, gap = 22, pad = 28;
  const sheetW = cols * cell + (cols - 1) * gap + pad * 2;
  const sheet = await browser.newPage({ viewport: { width: sheetW, height: 800 } });
  // load via goto(file://) with relative img src — file:// subresources are
  // blocked on a setContent data-origin page, so write the sheet to disk first.
  const imgs = files.map((f, i) =>
    `<figure><img src="${path.basename(f)}"><figcaption>${String(i + 1).padStart(2, "0")}</figcaption></figure>`).join("");
  const sheetHtml = `<body style="margin:0;background:#161618;padding:${pad}px;font-family:-apple-system,sans-serif">
     <div style="display:grid;grid-template-columns:repeat(${cols},${cell}px);gap:${gap}px">${imgs}</div>
     <style>figure{margin:0}img{width:${cell}px;display:block;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.4)}
     figcaption{color:#8a8a93;font-size:13px;padding:8px 2px;font-variant-numeric:tabular-nums}</style></body>`;
  const sheetHtmlPath = path.join(outDir, "_sheet.html");
  fs.writeFileSync(sheetHtmlPath, sheetHtml);
  await sheet.goto("file://" + sheetHtmlPath, { waitUntil: "networkidle" });
  const sheetPath = path.join(outDir, "contact_sheet.png");
  await sheet.screenshot({ path: sheetPath, fullPage: true });
  fs.unlinkSync(sheetHtmlPath);

  await browser.close();
  writeCaption(manifest, outDir);
  console.log(`[carousel] caption -> ${path.join(outDir, "caption.md")}`);
  console.log(`[carousel] contact sheet -> ${sheetPath}`);
  if (args.open) openFile(sheetPath);
}

main().catch((e) => { console.error("[carousel] error:", e); process.exit(1); });
