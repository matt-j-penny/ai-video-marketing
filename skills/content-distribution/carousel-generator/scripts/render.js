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

/* ---- video slides: play a source clip inside the slide (ffmpeg) ----------
   slide.video = { start, duration, src?, crop?: "W:H:X:Y", speed?, audio?: {src, start} }
   media       -> clip fills the .media__img box (rounded, cover-fit) over the rendered PNG
   cover_image -> clip full-bleed under the scrim + text; the swipe arrow eases right and back */
function renderVideoSlide(job, manifest, manifestDir, outDir) {
  const { execFileSync } = require("child_process");
  const v = job.v, rel = p => path.isAbsolute(p) ? p : path.resolve(manifestDir, p);
  const src = rel(v.src || manifest.source_video || "");
  if (!fs.existsSync(src)) { console.warn(`[carousel] slide ${job.nn}: video source not found ${src}`); return; }
  const speed = v.speed || 1, dur = v.duration * speed;
  const out = path.join(outDir, `slide_${job.nn}.mp4`);
  const ff = a => execFileSync("ffmpeg", ["-nostdin", "-loglevel", "error", "-y", ...a]);
  const crop = v.crop ? `crop=${v.crop},` : "";
  const clipChain = (w, h) => `[1:v]${crop}setpts=${speed}*PTS,scale=${w}:${h}:force_original_aspect_ratio=increase,crop=${w}:${h},fps=30`;
  const ins = [], extra = [];
  let fc;
  if (job.kind === "media") {
    const { x, y } = job.rect, w = Math.round(job.rect.w / 2) * 2, h = Math.round(job.rect.h / 2) * 2, r = job.rect.r;
    const mask = path.join(outDir, `.mask_${job.nn}.png`); extra.push(mask);
    ff(["-f", "lavfi", "-i", `color=white:s=${w}x${h},format=gray`, "-frames:v", "1", "-vf",
      `geq=lum='if(gt(abs(X-${w}/2+0.5),${w}/2-${r})*gt(abs(Y-${h}/2+0.5),${h}/2-${r}),if(lte(hypot(abs(X-${w}/2+0.5)-(${w}/2-${r}),abs(Y-${h}/2+0.5)-(${h}/2-${r})),${r}),255,0),255)'`, mask]);
    ins.push("-loop", "1", "-i", job.base, "-ss", v.start, "-t", v.duration, "-i", src, "-loop", "1", "-i", mask);
    fc = `[0:v]scale=${W}:${H}[b];${clipChain(w, h)}[c];[2:v]format=gray[m];[c][m]alphamerge[cm];[b][cm]overlay=${Math.round(x)}:${Math.round(y)}:shortest=1[v0]`;
  } else {
    extra.push(job.fg, job.arrow);
    ins.push("-f", "lavfi", "-i", `color=black:s=${W}x${H}`, "-ss", v.start, "-t", v.duration, "-i", src, "-loop", "1", "-i", job.fg, "-loop", "1", "-i", job.arrow);
    fc = `${clipChain(W, H)}[c];[0:v][c]overlay=0:0:shortest=1[b0];[2:v]scale=${W}:${H}[f];[b0][f]overlay[b1];`
       + `[3:v]scale=${W}:${H}[a];[b1][a]overlay=x='9*(1-cos(2*PI*t))/2':y=0[v0]`;
  }
  fc += ";[v0]format=yuv420p[v]";
  let maps = ["-map", "[v]", "-an"];
  if (v.audio && v.audio.src) {
    ins.push("-ss", v.audio.start || 0, "-t", dur, "-i", rel(v.audio.src));
    const ai = job.kind === "media" ? 3 : 4;
    fc += `;[${ai}:a]afade=t=out:st=${Math.max(0, dur - 0.4)}:d=0.4[a]`;
    maps = ["-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "160k"];
  }
  try {
    ff([...ins.map(String), "-filter_complex", fc, ...maps, "-t", String(dur), "-c:v", "libx264", "-crf", "18", "-movflags", "+faststart", out]);
    console.log(`[carousel] video slide -> ${out}`);
  } catch (e) {
    console.warn(`[carousel] slide ${job.nn}: ffmpeg failed (is ffmpeg installed?) ${e.stderr || e.message}`);
  } finally { extra.forEach(f => fs.existsSync(f) && fs.unlinkSync(f)); }
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

  const files = [], videoJobs = [];
  const clip = { x: 0, y: 0, width: W, height: H };
  for (let i = 0; i < nSlides; i++) {
    // isolate slide i at 0,0 so a clip screenshot is pixel-exact
    await page.evaluate((idx) => {
      const deck = document.getElementById("deck");
      deck.style.cssText = "padding:0;gap:0;display:block";
      document.querySelectorAll(".slide").forEach((s, j) => { s.style.display = j === idx ? "flex" : "none"; });
      window.scrollTo(0, 0);
    }, i);
    const nn = String(i + 1).padStart(2, "0");
    const file = path.join(outDir, `slide_${nn}.png`);
    await page.screenshot({ path: file, clip });
    files.push(file);

    const s = manifest.slides[i];
    if (!s || !s.video) continue;
    if (s.type === "media") {
      const rect = await page.evaluate(() => {
        const el = document.querySelector('.slide:not([style*="display: none"]) .media__img');
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { x: r.x, y: r.y, w: r.width, h: r.height, r: parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0 };
      });
      if (rect) videoJobs.push({ kind: "media", nn, base: file, rect, v: s.video });
      else console.warn(`[carousel] slide ${nn}: video needs an image box (set "image" to a frame of the clip)`);
    } else if (s.type === "cover_image") {
      // two transparent layers over a full-bleed clip: everything but the image, and the swipe arrow alone
      const layer = async (name, css) => {
        await page.addStyleTag({ content: css }).then(h => h.evaluate(e => e.id = "vidlayer"));
        const p = path.join(outDir, `.${name}_${nn}.png`);
        await page.screenshot({ path: p, clip, omitBackground: true });
        await page.evaluate(() => document.getElementById("vidlayer").remove());
        return p;
      };
      const clear = "html,body,.slide{background:transparent!important}.slide__bg,.slide__media{display:none!important}";
      const fg = await layer("fg", clear + ".swipe .arrow{visibility:hidden}");
      const arrow = await layer("arrow", clear + ".slide *{visibility:hidden}.swipe .arrow{visibility:visible}");
      videoJobs.push({ kind: "cover", nn, fg, arrow, v: s.video });
    } else console.warn(`[carousel] slide ${nn}: video is supported on cover_image and media slides only`);
  }
  console.log(`[carousel] rendered ${files.length} slides @ ${W * args.scale}x${H * args.scale} -> ${outDir}`);
  for (const j of videoJobs) renderVideoSlide(j, manifest, manifestDir, outDir);

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
