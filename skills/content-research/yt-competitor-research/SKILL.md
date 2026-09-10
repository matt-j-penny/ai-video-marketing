---
name: yt-competitor-research
description: "Scans YouTube competitors via yt-dlp (free, no browser, no Apify), then deep-breaks-down the winners' packaging. Same research logic as ig-competitor-research: pulls each channel's last-week uploads (default: first 5 channels in competitor-list.md), keeps the top 3 by views per channel, pools and ranks the whole set by views, and scores each video's breakout (its views vs that channel's own weekly median) so true outliers surface regardless of channel size. Then fans out one subagent per pick to analyze the title + thumbnail (no frame extraction, no transcription — packaging is the unit of analysis): title archetype, thumbnail visual breakdown, title↔thumb packaging gap, one-line concept, and why it worked. Builds a self-contained, visual HTML report in research/ and opens it automatically. Triggers: youtube competitor research, yt competitor research, yt research, what's working on youtube, youtube outliers, research yt competitors, youtube niche research."
metadata:
  version: 1.0.0
  last_updated: 2026-09-10
---

# YT Competitor Research — Top 3 / Channel From the Last Week, Packaging Broken Down

Same shape as `ig-competitor-research` — last-week window, top 3 per creator, pooled ranking, per-creator breakout — with yt-dlp in place of Apify. Three phases, and the orchestrator (you) stays light the whole way — **scripts do the ranking, scoring, formatting, and report assembly; you never sort videos in your head, hand-format a view count, hand-author the report manifest, or read a raw yt-dlp blob.**

- **Phase 1 — Scrape & prep:** yt-dlp pulls each channel's 20 newest upload URLs (a buffer that comfortably covers a week), then fetches full metadata for every candidate in parallel; `rank-and-select.py` enforces the 7-day window, ranks the survivors, scores each one's **breakout** (views vs its channel's weekly median), picks the winners, and writes `selection.json` + scatters each pick's thumbnail URL and description into its job dir.
- **Phase 2 — Break down:** one Sonnet subagent per pick downloads its thumbnail, looks at it, and **writes `<jobdir>/post.json`** (the packaging analysis). Thumbnails never touch your context.
- **Phase 3 — Build:** you write one `pattern.txt` synthesis line; `build-report.py` assembles `selection.json` + every `post.json` + `pattern.txt` into a self-contained, visual HTML report and opens it.

**Ranking is by VIEWS.** Likes break ties. Live streams and premieres report `view_count: null` until they end — the script drops them automatically, along with anything older than the 7-day window.

**Breakout score = views ÷ that channel's weekly median.** Per-channel (median across its uploads in the window), so a small channel's overperformer isn't buried under a big channel's median-level video. Computed in `rank-and-select.py`, shown as a 🔥/📈 badge on every card. (Ranking still uses raw views — breakout is a surfaced signal, not the sort key.)

**Packaging is the unit of analysis.** For long-form, the title IS the hook and the thumbnail is the other half of the click decision. No video download, no frame extraction, no transcription — the subagents analyze title + thumbnail (+ description for context) only. That's what makes this skill fast and free.

**Claude reads the thumbnails directly.** Analyzed in-house by the subagents (native multimodal Read) — no external vision API, no extra key.

---

## Freshness Check

Compare `last_updated` above to today's date. If more than 2 weeks have passed, tell the user this skill file may be out of date and suggest re-pulling/reinstalling the `ai-video-marketing` repo (`git pull`, or re-running whichever install command they used) before relying on it — then continue with the workflow below regardless.

## Prerequisites

- **`yt-dlp`** installed and on PATH (`./setup.sh` from the project root installs it). Already used by `transcribe-url`. Update if it warns about being >90 days old: `brew upgrade yt-dlp` (macOS), `winget upgrade yt-dlp.yt-dlp` (Windows), `uv tool upgrade yt-dlp` (Linux / uv installs).
- **`uv`** — builds the report builder's pillow venv once (`~/.cache/content-os/pillow-venv`, sentinel-gated; `CONTENT_OS_PILLOW_VENV` overrides). Python and `curl` assumed present (`./setup.sh` checks all of it).
- **A `competitor-list.md`** in the project root with a `## YouTube` section listing channels via `youtube.com/@handle` URLs (with or without a trailing `/videos`).
- Shell steps are bash/awk/xargs: macOS, Linux, Windows via Git Bash. The finished report opens in your default browser (macOS / Windows / Linux, via Python's `webbrowser`).

---

## PHASE 1 — Scrape & Prep (you, the orchestrator)

1. **Resolve handles.** Read `competitor-list.md`, find `## YouTube`, extract `@handle`s from the `youtube.com/@handle` URLs (a trailing `/videos` is fine, ignore it), and **default to the first 5** (order = priority — don't ask). **Skip any `###` block whose heading starts with `EXAMPLE`** (placeholder blocks from the template, never real channels). Inline handles override the default; "all" uses every handle. If the section is empty after dropping EXAMPLE blocks and no inline handles were given, ask for channels.
2. **Stamp a unique run.** Run `date +%Y-%m-%d_%H%M%S` once and call it `<RUN>` (e.g. `2026-06-09_153012`). `<RUN_DIR>` = `/tmp/yt-research/<RUN>/`; `mkdir -p "<RUN_DIR>/urls"`. `<DATE>` = the `YYYY-MM-DD` part. Final report = `<project_root>/research/YT-Competitor-Research_<RUN>.html` (create `research/` if missing). **Every run is its own isolated dir + its own report file** — the timestamp guarantees zero collision, so never inspect, reuse, wipe, or worry about anything from a prior run. **Shell state doesn't persist between Bash calls — substitute the literal `<RUN_DIR>` path into every command below; never rely on a `$RUN_DIR` variable surviving.**
3. **Pull candidate URLs (per channel).** One Bash call — a `yt-dlp --version` pre-check (a missing yt-dlp fails loudly here instead of producing empty URL files), then a single-line `for` loop, one operation in the body. yt-dlp's stderr stays visible on this pull so a broken/rate-limited yt-dlp is distinguishable from a dead channel:

   ```bash
   yt-dlp --version && for h in handle_a handle_b handle_c handle_d handle_e; do yt-dlp --flat-playlist --print url --playlist-end 20 "https://www.youtube.com/@${h}/videos" > "<RUN_DIR>/urls/${h}.txt"; done; wc -l "<RUN_DIR>/urls/"*.txt
   ```

   Few hundred ms per channel — don't parallelize this step; the per-video fetch is the heavy lift. **20 newest is a buffer, not the window** — flat-playlist entries carry no upload dates, so the week filter happens in `rank-and-select.py` after the metadata fetch (20/week caps even a daily poster, mirroring the IG skill's `resultsLimit: 20`). The `/videos` tab is chronological newest-first for yt-dlp (no cookies, so YouTube can't serve a sticky "Popular" sort) and excludes Shorts. If a handle's URL file is empty AND yt-dlp printed no error for it, the channel doesn't exist or has no public uploads — note it, continue with the rest. If yt-dlp printed an error (extractor break, HTTP 429), that's a tool problem, not a dead channel: surface it.
4. **Build the handle+URL TSV.** Use `awk` over the URL files — **never a nested `for ... while read ...` shell loop** (silently rejected by the harness):

   ```bash
   awk 'FNR==1{h=FILENAME; sub(/.*\//,"",h); sub(/\.txt$/,"",h)} {print h"\t"$0}' "<RUN_DIR>/urls/"*.txt > "<RUN_DIR>/all_urls.tsv" && wc -l "<RUN_DIR>/all_urls.tsv"
   ```

5. **Parallel-fetch full metadata.** One JSON file per video at `meta/<handle>/<videoId>.json`:

   ```bash
   awk -F'\t' '{print $1, $2}' "<RUN_DIR>/all_urls.tsv" | xargs -P 20 -L 1 sh -c 'h=$1; u=$2; id=$(echo "$u" | grep -oE "v=[^&]+" | cut -d= -f2); mkdir -p "<RUN_DIR>/meta/$h"; yt-dlp -J --skip-download "$u" 2>/dev/null > "<RUN_DIR>/meta/$h/$id.json"' _ ; find "<RUN_DIR>/meta" -name "*.json" | wc -l
   ```

   `-P 20` is the sweet spot — higher risks YT rate-limiting (HTTP 429). Set Bash `timeout: 300000` (5 min); 100 videos parallelized 20-wide clears in ~30s, but allow headroom for larger channel lists. A failed fetch leaves an empty JSON file — `rank-and-select.py` flags and skips it.
6. **Rank, score & prep (ONE script — no in-head sorting, no jq).** Run:

   ```
   python3 <SKILL_DIR>/scripts/rank-and-select.py "<RUN_DIR>/meta" "<RUN_DIR>" --per-handle 3 --expect "handle_a,handle_b,handle_c,handle_d,handle_e"
   ```

   (`python` instead of `python3` on Windows Git Bash.) It parses every raw yt-dlp JSON locally, **keeps only videos uploaded in the last 7 days** (`--days` overrides), drops null-view entries (live/premieres) and failed fetches, ranks the survivors by views (likes break ties), keeps the top 3 per channel, pools and sorts the whole set, computes each pick's **breakout score** (its views ÷ that channel's weekly median), then writes `<RUN_DIR>/selection.json` and scatters each pick's `thumburl.txt` (best jpg thumbnail) + `description.txt` (full description, verbatim) into `<RUN_DIR>/<rank>_<handle>/`. It prints a ranked table (with the breakout column) to stderr and flags any `--expect` handle with nothing in the window. **Read its stderr** — relay the table and note any empty handle in the Pattern line later. (Stdlib only — plain system Python, no `uv`.)

`<SKILL_DIR>` = this skill's own folder — use the absolute "Base directory for this skill" path shown when the skill launches (do **not** hardcode a machine-specific path).

Then go to Phase 2. You now have `selection.json` (small) as your single source of truth — you never read a raw yt-dlp blob.

---

## PHASE 2 — Break Down Each Video (fan out: one subagent per pick)

Read `<RUN_DIR>/selection.json`. For each pick, spawn a **Sonnet subagent** (Agent tool, `subagent_type: "general-purpose"`, `model: "sonnet"`). **Spawn them in parallel — batch the Agent calls in single messages** so they run concurrently. Each subagent downloads its thumbnail, analyzes the packaging, **writes `<jobdir>/post.json`**, and returns one short status line (so you can write the Pattern without reading any files). Substitute every `<…>` with the real value from `selection.json` before spawning.

Prompt template:

> You are breaking down ONE YouTube video's packaging for a competitor-research report. You analyze the title + thumbnail only — there is no video download or transcript step.
> Video: rank #<rank>, @<handle>, "<title>", <views> views, <likes> likes, <like_rate> like rate, <duration>, posted <date>.
> URL: <url>
> Job dir: <jobdir>
>
> 1. Run exactly (the thumbnail URL is saved in the job dir):
>    `bash <SKILL_DIR>/scripts/fetch-thumb.sh "<jobdir>"`
> 2. Read `<jobdir>/thumb.jpg` (the Read tool renders images — actually look at it) and `<jobdir>/description.txt` (context for what the video is). Leave every file in place; delete nothing.
> 3. Write `<jobdir>/post.json` using the Write tool, as VALID JSON with exactly these keys:
>    `{"rank": <rank>, "title_archetype": "<the title's hook structure in 2-4 words: result + timeframe, negative warning, curiosity-gap how-to, listicle, us-vs-them, income claim, challenge, etc.>", "thumb_breakdown": "<1-2 sentences: what's visually on the thumbnail — face/expression, objects, composition, colors, arrows — plus any on-thumb text VERBATIM in quotes (or note there's no text)>", "packaging": "<ONE sentence: how the title and thumbnail work together — what gap or promise makes the click>", "breakdown": "<ONE sentence: what the video actually is / its concept, inferred from title + description>", "why": "<1-2 sentences grounded in the real title archetype + thumbnail mechanics — the actual packaging mechanic, not generic praise>"}`
>    Make sure it parses: escape inner quotes, no trailing commas, keep each value on one line. If the thumbnail download failed, set "thumb_breakdown" to "(unavailable)", base "packaging"/"why" on the title alone, and still write the file.
> 4. Return ONLY one status line, nothing else:
>    `OK #<rank> @<handle> | archetype: <title_archetype> | why: <why, ≤18 words>`
>    (or `FAIL #<rank> @<handle> | <one-line reason>` if the thumbnail download failed.)

---

## PHASE 3 — Build the HTML Report & Open It (you, the orchestrator)

1. **Write the Pattern line.** From the returned status lines (archetype + why per pick), write **3-4 short, punchy sentences MAX** on what repeats across the pool — lead with the takeaway, no preamble, scannable in ~5 seconds. Hit the highest-signal threads only (dominant title archetype, the thumbnail mechanic that recurs, the topic cycle, the biggest breakout). Don't catalog every video or quote every stat. Note any handle `rank-and-select.py` flagged as empty. Put it in **one `Write` call** to `<RUN_DIR>/pattern.txt` (plain text). (`<RUN_DIR>` is fresh per run, so there's never a stale `pattern.txt` to overwrite.)
2. **Assemble + render + open (ONE command).** Run:

   ```
   bash <SKILL_DIR>/scripts/build-report.sh "<RUN_DIR>" "<project_root>/research/YT-Competitor-Research_<RUN>.html" --open
   ```

   `build-report.sh` runs `build-report.py` on the shared pillow venv (`~/.cache/content-os/pillow-venv`; built once by `uv` on first use, sentinel-gated on `.deps-ok`, `CONTENT_OS_PILLOW_VENV` overrides). Pointed at the **directory**, `build-report.py` assembles the manifest itself — `selection.json` is authoritative for the scraped + computed facts (rank, handle, title, views, likes, like rate, date, duration, url, breakout), each `<jobdir>/post.json` supplies the analysis, `<jobdir>/description.txt` supplies the collapsible description, `pattern.txt` supplies the synthesis — then downscales + base64-embeds every thumbnail, writes the HTML (with breakout badges), leaves an inspectable `manifest.json` in `<RUN_DIR>`, and `--open` pops it in the browser. It prints the path and **warns on stderr if any pick was missing a usable `post.json`**.
3. **If a pick was flagged missing**, re-spawn just that one subagent (it re-writes its `post.json`), then re-run the build command. Otherwise you're done.
4. **Report the file path** back to the user — `research/YT-Competitor-Research_<RUN>.html` — plus the ranked table (with breakout) and the one-paragraph pattern.

RULES:
- **For long-form, the title IS the hook** — never substitute a description line or invent a spoken hook. The thumbnail is the other half of the packaging; the subagents analyze both together.
- **Why it worked is grounded** in the real title + thumbnail. One sharp mechanic beats a paragraph of praise. Never invent a view count or engagement rate.
- HTML is the only output. No markdown report. Scraped + computed facts always win over a subagent's echoed numbers (the builder enforces this).

---

## Rules of Thumb
- **yt-dlp end to end — free, no browser, no Apify.** No cookies means YouTube can't serve a sticky "Popular" sort; `/videos` is chronological newest-first and excludes Shorts. Eliminates the whole hidden-tab / DOM-drift / sticky-sort failure class. If yt-dlp breaks, surface it — don't reach for Apify, browser scraping, or other fallbacks.
- **Scripts own the mechanical work, you own the judgment.** You never sort videos, compute a score, format a count/date, or hand-author a manifest. `rank-and-select.py` ranks + scores + preps; subagents write `post.json`; `build-report.py` assembles + renders. You only resolve handles, stamp the run, run three bash steps, fan out, and write one Pattern line.
- **Default 5 channels, top 3 each.** 3 channels → 9 videos, 5 → 15 — same as the IG skill. Order in `competitor-list.md` = priority. A channel with no uploads in the window just contributes fewer (flagged by `--expect`).
- **Week window, enforced in the script.** Pull 20 newest per channel as a buffer (flat-playlist has no dates), then `rank-and-select.py` keeps only uploads from the last 7 days — signal on what's working *now*, not the channel's all-time hits. `--days` overrides if the user asks for a different window; don't change the default.
- **Rank by views; surface breakout.** Likes break ties. Breakout = views ÷ channel's weekly median (per-channel, robust to channel size — mirrors the IG skill's likes-vs-weekly-median). All computed in `rank-and-select.py`, badged on every card.
- **Subagents do the thumbnails, not you.** One Sonnet agent per pick, spawned in parallel; each writes `post.json` and returns a one-line status. Images stay out of the orchestrator context.
- **Output is a self-contained HTML report** built by `build-report.py` (Pillow downscales + base64-embeds every thumbnail — portable, no asset folder, no expiring links). Breakout badges, collapsible copy-able descriptions, Watch-on-YouTube buttons, 📺 favicon. `--open` pops it in the browser.
- **Resilient assembly.** A pick whose `post.json` is missing/malformed still renders (thumb + facts + breakout), flagged on stderr — re-spawn that one subagent and re-run the build. Nothing else is lost.
- yt-dlp must be reasonably fresh. The `>90 days old` warning is harmless, but YouTube's extractor changes — if a channel suddenly returns nothing, update yt-dlp first before assuming the channel's gone.
- Create `research/` if missing. Don't inspect or clean up prior reports — every run writes a new dated file.
- Intermediates (`urls/`, `meta/`, `selection.json`, `thumb.jpg`, `post.json`, `pattern.txt`, `manifest.json`) live in `<RUN_DIR>` = `/tmp/yt-research/<RUN>/` — timestamped, so every run is fully isolated: no collisions, nothing to clean. The HTML in `research/` is the durable artifact.

## Bash hygiene (an earlier version of this skill burned a lot of cycles on this — read it)
- **Never nest shell loops in a single Bash call.** A `for` containing a `while IFS= read -r ...` (or any `do...done` inside another `do...done`) silently gets rejected by the harness with "user doesn't want to proceed" and no actual permission prompt to the user. The user just sees you hang.
- **Iterate with `awk` or `find | xargs`, not nested `for/while`.** Step 4's awk-with-FILENAME is the canonical pattern: zero shell loops, derives the handle from the filename.
- **Single-line `for` loops with one operation in the body are fine.** Step 3 uses `for h in ...; do <one command>; done` — that pattern passes.
- **Keep each Bash call atomic — one logical step.** Don't chain "pull URLs then fetch metadata then rank" in one giant `&&` block. Each step gets its own Bash tool call so failures localize and the user can see progress.
- If a Bash call comes back with "user doesn't want to proceed" but the user says they got no prompt, the command shape is the problem — simplify and split, don't retry the same call.
