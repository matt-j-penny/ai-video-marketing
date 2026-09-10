#!/usr/bin/env node
/* =============================================================================
   Carousel template library — save / list / scaffold reusable deck recipes.

   Templates live in ../templates/*.json (manifest skeletons: locked theme +
   font + cover concept + layout structure, with placeholder copy). Once a deck
   performs, save it as a template; later "do carousel v10 on this topic" is just
   `new <template> <slug>` + swapping the copy. Embedded base64 images are
   stripped on save so templates stay tiny.

   Usage:
     node library.js list
     node library.js new  <template> <slug> [--out PATH]
     node library.js save <manifest.json> <name>
============================================================================= */
const fs = require("fs");
const path = require("path");

const TEMPLATES_DIR = path.join(__dirname, "..", "templates");

function listTemplates() {
  if (!fs.existsSync(TEMPLATES_DIR)) { console.log("(no templates yet)"); return; }
  const files = fs.readdirSync(TEMPLATES_DIR).filter((f) => f.endsWith(".json")).sort();
  if (!files.length) { console.log("(no templates yet)"); return; }
  for (const f of files) {
    const name = f.replace(/\.json$/, "");
    let m = {};
    try { m = JSON.parse(fs.readFileSync(path.join(TEMPLATES_DIR, f), "utf8")); } catch { /* skip bad */ }
    const types = (m.slides || []).map((s) => s.type || "statement").join(" -> ");
    console.log(`• ${name}`);
    console.log(`    ${m.topic || "(no topic)"}  [${m.theme || "midnight"}/${m.font || "character"}]`);
    if (types) console.log(`    ${types}`);
  }
}

// never carry megabytes of base64 into a template — blank embedded covers/images.
function stripImages(m) {
  for (const s of m.slides || []) {
    if (typeof s.image === "string" && s.image.startsWith("data:")) s.image = "";
  }
  return m;
}

function saveTemplate(manifestPath, name) {
  if (!manifestPath || !name) {
    console.error("usage: node library.js save <manifest.json> <name>"); process.exit(1);
  }
  const m = stripImages(JSON.parse(fs.readFileSync(manifestPath, "utf8")));
  fs.mkdirSync(TEMPLATES_DIR, { recursive: true });
  const dest = path.join(TEMPLATES_DIR, `${name}.json`);
  fs.writeFileSync(dest, JSON.stringify(m, null, 2) + "\n");
  console.log(`[library] saved template -> ${dest}`);
}

function newFromTemplate(name, slug, outArg) {
  if (!name || !slug) {
    console.error("usage: node library.js new <template> <slug> [--out PATH]"); process.exit(1);
  }
  const src = path.join(TEMPLATES_DIR, `${name}.json`);
  if (!fs.existsSync(src)) {
    console.error(`[library] no template '${name}'. Run: node library.js list`); process.exit(1);
  }
  const m = JSON.parse(fs.readFileSync(src, "utf8"));
  m.slug = slug;
  // default: carousel/outputs/<slug>/carousel.json under the cwd (run from the
  // project root) so the manifest lives beside its cover/ variants and rendered PNGs.
  const out = outArg || path.join("carousel", "outputs", slug, "carousel.json");
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(m, null, 2) + "\n");
  console.log(`[library] scaffolded '${name}' -> ${out}`);
  console.log("[library] swap the copy + cover.concept, run cover.py, then render.js.");
}

const argv = process.argv.slice(2);
const cmd = argv.shift();
let outArg;
const outIdx = argv.indexOf("--out");
if (outIdx >= 0) { outArg = argv[outIdx + 1]; argv.splice(outIdx, 2); }

if (cmd === "list") listTemplates();
else if (cmd === "save") saveTemplate(argv[0], argv[1]);
else if (cmd === "new") newFromTemplate(argv[0], argv[1], outArg);
else {
  console.error("usage: node library.js <list|save|new>\n"
    + "  list\n"
    + "  new  <template> <slug> [--out PATH]\n"
    + "  save <manifest.json> <name>");
  process.exit(1);
}
