---
name: ig-competitor-research
description: "Scans Instagram competitors via the Apify MCP (apify/instagram-post-scraper), then deep-breaks-down the winners. Pulls each handle's last-week posts (pinned excluded), keeps the top 3 by likes per handle across all formats, pools and ranks the whole set by likes (3 handles = 9 posts, 5 = 15), and scores each post's breakout (its likes vs that creator's own weekly median) so true outliers surface regardless of account size. Then fans out one subagent per post: reels get downloaded + Whisper-transcribed + keyframe analysis; carousels/images get slide-by-slide analysis. Each post is broken down into hook (+ hook type: spoken vs on-screen text), content format (talking head / listicle / side-by-side / reaction / …), full transcript, a one-line concept breakdown, and why it worked. Builds a self-contained, visual HTML report (media auto-fits each post's real aspect ratio — no black bars — swipeable carousels, reel keyframe galleries, one-click-copy transcripts, breakout badges, View-on-Instagram links) in research/ and opens it automatically. Triggers: content research, competitor research, what's trending, niche research, research competitors, find outliers, trending content, what's working in my niche."
metadata:
  version: 1.0.0
  last_updated: 2026-09-10
---

# IG Competitor Research — Top 3 / Handle, Transcribed + Visually Broken Down

Three phases, and the orchestrator (you) stays light the whole way — **scripts do the ranking, scoring, formatting, media routing, and report assembly; you never sort posts in your head, hand-format a date, hand-author the report manifest, or pull media blobs into context.**

- **Phase 1 — Scrape & prep:** one paid Apify call → pull the dataset to disk via the MCP (`get-dataset-items`) → `rank-and-select.py` ranks the posts, scores each one's **breakout** (likes vs its creator's weekly median), picks the winners, and writes `selection.json` + scatters each post's media URL into its job dir.
- **Phase 2 — Break down:** one Sonnet subagent per pick downloads its media, transcribes/analyzes it, and **writes `<jobdir>/post.json`** (the analysis). Heavy media never touches your context.
- **Phase 3 — Build:** you write one `pattern.txt` synthesis line; `build-report.py` assembles `selection.json` + every `post.json` + `pattern.txt` into a self-contained, visual HTML report and opens it.

**Ranking is by LIKES, not views.** This actor returns no view/play count — likes is the rank key, comments break ties, hidden likes (`-1`) sort last. `rank-and-select.py` enforces all of this; don't re-derive it.

**Breakout score = likes ÷ that creator's weekly median.** Per-creator, so a small account's overperformer isn't buried under a big account's median-level post. Computed in `rank-and-select.py`, shown as a 🔥/📈 badge on every card. (Ranking still uses raw likes — breakout is a surfaced signal, not the sort key.)

**All formats compete.** Reels, carousels, and images are ranked together — top post is top post, whatever the format. Each pick is tagged with its format and routed to the matching breakdown branch automatically.

**Claude reads the media directly.** Keyframes and carousel slides are analyzed in-house by the subagents (native multimodal Read) — no external vision API, no extra key.

---

## Freshness Check

Compare `last_updated` above to today's date. If more than 2 weeks have passed, tell the user this skill file may be out of date and suggest re-pulling/reinstalling the `ai-video-marketing` repo (`git pull`, or re-running whichever install command they used) before relying on it — then continue with the workflow below regardless.

## PHASE 1 — Scrape & Prep (you, the orchestrator)

1. **Resolve handles.** Read `competitor-list.md`, find `## Instagram`, extract handles from the `instagram.com/handle/` URLs, and **default to the first 5** (order = priority — don't ask). **Skip any block whose `###` heading starts with `EXAMPLE`** (placeholder rows from the template, not real accounts). Inline handles override the default; "all" uses every handle. If the section has no real handles left (empty, or only EXAMPLE blocks) and none were given inline, stop and ask for handles.
2. **Stamp a unique run.** Run `date +%Y-%m-%d_%H%M%S` once and call it `<RUN>` (e.g. `2026-06-04_153012`). `<RUN_DIR>` = `/tmp/ig-research/<RUN>/`; `mkdir -p` it. `<DATE>` = the `YYYY-MM-DD` part. Final report = `<project_root>/research/IG-Competitor-Research_<RUN>.html` (create `research/` if missing). **Every run is its own isolated dir + its own report file** — the timestamp guarantees zero collision, so never inspect, reuse, wipe, or worry about anything from a prior run.
3. **Run the actor (ONE paid call, all handles).** Load the Apify tool via `ToolSearch` → `select:mcp__Apify__call-actor`. (`Apify` in these tool names is the MCP **server alias** — on a machine where the server was registered under a different alias the exact `select:` returns nothing; run `ToolSearch` with keyword `call-actor` instead and use the `mcp__<alias>__call-actor` it returns. The same alias applies to `get-actor-run` and `get-dataset-items` below.) Call the tool with `actor: "apify/instagram-post-scraper"`, `waitSecs: 0`, and this exact input, substituting the resolved handles into `username`:

   ```json
   {
     "dataDetailLevel": "detailedData",
     "onlyPostsNewerThan": "1 week",
     "resultsLimit": 20,
     "skipPinnedPosts": true,
     "username": ["handle_a", "handle_b", "handle_c"]
   }
   ```

   `username` takes an array — every handle in one run.

   **Fire it start-and-return — never blocking.** `call-actor` waits up to `waitSecs` (default 30, max 45) for the run to finish; a 5-handle `detailedData` run takes a few minutes, so a blocking call just burns its wait and hands back a non-terminal run anyway. **Always pass `waitSecs: 0`**: the call returns instantly with a `runId`. Don't hunt for a `datasetId` in that response — you capture it from the finished run in the next breath. **This is the only paid call.** `detailedData` returns direct media for every format (reel `videoUrl`, carousel `images[]`), so this one scrape covers both ranking AND downloads. (~$0.003/post; ~$0.11 for 3 handles, ~$0.18 for 5.)

   **Then poll until it finishes.** Load the run-status tool: `ToolSearch` → `select:mcp__Apify__get-actor-run`. The tool does the waiting for you: call it with the `runId` and `waitSecs: 45` — it blocks up to 45s and returns as soon as the run goes terminal (or with the current status if not yet). Just call it again back-to-back until `status` is `SUCCEEDED` — no `sleep` dance needed. Then **capture the `datasetId` from that response** (it's in `storages`, and the response's `nextStep` line interpolates it for you) — that's what the next step pulls. If `status` comes back `FAILED`, `ABORTED`, or `TIMED-OUT`, stop and report the run — never pull a dead run. (A 5-handle run typically clears in 2–5 polls.)
4. **Pull the dataset to disk via the MCP.** Load the tool: `ToolSearch` → `select:mcp__Apify__get-dataset-items`. Then call `mcp__Apify__get-dataset-items` with **only** these two args — **no `fields` filter** (it defaults to `limit: 20`, so the explicit `limit` matters):

   ```
   datasetId: "<DATASET_ID>"
   limit:     200
   ```

   This rides the same OAuth that ran the paid scrape — **no token, ever: never look for an API token or env var and never ask the user to paste or `export` one; this skill has no key-based code path.**

   **Omitting `fields` is what forces the result onto disk — do not add it back.** A field-trimmed pull is small enough that the harness hands it back *inline* (in your context) on a light week, which would force you to hand-retype 1,000-char signed URLs (a mistyped char silently breaks the download — `--expect-count` only catches a *dropped* record, not a *mangled* one). Pulling the **full** records (~12K chars/post) reliably blows past the tool-result token cap, so the harness auto-spills the *entire* result to `…/<session-id>/tool-results/mcp-Apify-get-dataset-items-<ts>.txt` and returns that path instead of the blob. **Never read the spill into context.** Extract the items straight to disk with `jq` (zero tokens spent on the URLs/captions):

   ```bash
   jq '.items' "<SPILLED_FILE>" > "<RUN_DIR>/dataset.json"
   ```

   `.items` is the bare array step 5 wants; `<N>` = `jq -r '.itemCount' "<SPILLED_FILE>"` (if the envelope has no `itemCount`, `<N>` comes back as `null` and `--expect-count` simply skips the guard; that's fine, the guard only adds value on the hand-written inline path below). **No handle-filtering here** — `rank-and-select.py` is authoritative on the `--expect` roster and drops any stray handle the actor slips in (a tagged/collab post), so `dataset.json` holds the full pull verbatim and `--expect-count <N>` still guards the whole write.

   **If it *still* returns inline** (only on a very light week — a handful of total posts): do **not** hand-retype URLs. Re-call `get-dataset-items` once with the same args to force the spill. Only if a genuinely tiny pull refuses to overflow, write the few inline records verbatim to `<RUN_DIR>/dataset.json` with the Write tool, then confirm `jq -r '.[] | (.videoUrl // empty), (.displayUrl // empty), (.images[]? // empty)' "<RUN_DIR>/dataset.json" | grep -vc '^https' || true` prints `0` (every media URL intact; the `|| true` is because `grep -c` exits 1 on zero matches, which is the success case here) before continuing.
5. **Rank, score & prep (ONE script — no in-head sorting).** Run (`python3` on macOS/Linux, `python` on Windows):

   ```
   python3 <SKILL_DIR>/scripts/rank-and-select.py "<RUN_DIR>/dataset.json" "<RUN_DIR>" --per-handle 3 --expect "handle_a,handle_b,handle_c" --expect-count <N>
   ```

   It groups by handle, ranks by likes (hidden last, ties by comments), keeps the top 3 per handle, pools and sorts the whole set, computes each pick's **breakout score** (its likes ÷ that handle's median likes this week), then writes `<RUN_DIR>/selection.json` and scatters each pick's media URL into `<RUN_DIR>/<rank>_<handle>/` (`videourl.txt` for reels, `imageurls.txt` for carousels/images). It prints a ranked table (with the breakout column) and flags any pick with a missing or malformed media URL or any `--expect` handle that returned nothing. **`--expect-count <N>`** (the count `get-dataset-items` returned) hard-errors if `dataset.json` doesn't hold exactly `<N>` items — catching any record dropped while writing the MCP result to disk (a non-numeric `<N>` such as `null` skips the guard with a note on stderr). **Read its stderr** — relay the table and note any empty handle in the Pattern line later. (Stdlib only — the system python, no `uv`.)

Then go to Phase 2. You now have `selection.json` (small) as your single source of truth — you never touched a media blob.

---

## PHASE 2 — Break Down Each Post (fan out: one subagent per pick)

Read `<RUN_DIR>/selection.json`. For each pick, spawn a **Sonnet subagent** (Agent tool, `subagent_type: "general-purpose"`, `model: "sonnet"`), choosing the template by `format`. **Spawn them in parallel — batch the Agent calls in single messages** so they run concurrently. Each subagent downloads its media into the job dir, analyzes it, **writes `<jobdir>/post.json`**, and returns one short status line (so you can write the Pattern without reading any files).

`<SKILL_DIR>` = this skill's own folder — use the absolute "Base directory for this skill" path shown when the skill launches (do **not** hardcode a machine-specific path). Substitute it, and every other `<…>`, with the real value from `selection.json` before spawning.

**Reel / Video** (`format` is `Reel` or `Video`) — prompt template:

> You are breaking down ONE Instagram reel for a competitor-research report.
> Post: rank #<rank>, @<handle>, <likes> likes, <comments> comments, posted <date>.
> Permalink: <url>
> Job dir: <jobdir>
> Caption: <caption>
>
> 1. Run exactly (the videoUrl is saved in the job dir):
>    `bash <SKILL_DIR>/scripts/reel-breakdown.sh "<jobdir>" "$(cat "<jobdir>/videourl.txt" 2>/dev/null)"`
>    (curls the reel from the saved videoUrl, grabs keyframes at 1s/2s/3s/midpoint, transcribes with faster-whisper small.en.)
> 2. Read `<jobdir>/transcript.md` and every `<jobdir>/frame_*.jpg` (the Read tool renders images — actually look at them). Leave every file in place; delete nothing.
> 3. Write `<jobdir>/post.json` using the Write tool, as VALID JSON with exactly these keys:
>    `{"rank": <rank>, "hook": "<the opening hook — the first spoken line verbatim from transcript.md, OR the on-screen text hook if a text overlay carries the open>", "hook_type": "<spoken | on-screen text | spoken + text — judge from frame_01s/02s/03s>", "content_format": "<the content format in 2-4 words: talking head, listicle, side-by-side comparison, reaction, screen-recording demo, voiceover b-roll, etc.>", "transcript": "<full transcript, one paragraph, verbatim>", "breakdown": "<ONE sentence: what the whole video actually is / its concept>", "why": "<1-2 sentences grounded in the hook + format + transcript — the actual mechanic, not generic praise>"}`
>    Make sure it parses: escape inner quotes, no trailing commas, keep each value on one line. If the download failed, set "transcript" to "(unavailable)", "hook_type"/"content_format" to "(unknown)", infer "hook"/"breakdown"/"why" from the caption, and still write the file.
> 4. Return ONLY one status line, nothing else:
>    `OK #<rank> @<handle> Reel | hook: <hook, ≤12 words> | why: <why, ≤18 words>`
>    (or `FAIL #<rank> @<handle> Reel | <one-line reason>` if the download failed.)

**Carousel / Image** (`format` is `Carousel` or `Image`) — prompt template:

> You are breaking down ONE Instagram <carousel|image> for a competitor-research report.
> Post: rank #<rank>, @<handle>, <likes> likes, <comments> comments, posted <date>.
> Permalink: <url>
> Job dir: <jobdir>
> Caption: <caption>
>
> 1. Run exactly (the image URLs are saved one-per-line in the job dir; the script reads the file itself):
>    `bash <SKILL_DIR>/scripts/fetch-images.sh "<jobdir>" "<jobdir>/imageurls.txt"`
> 2. Read every `<jobdir>/slide_*.jpg` in order (the Read tool renders images — actually look at them). Leave every file in place; delete nothing.
> 3. Write `<jobdir>/post.json` using the Write tool, as VALID JSON with exactly these keys:
>    `{"rank": <rank>, "hook": "<slide-1 headline / main on-image text>", "hook_type": "on-screen text", "content_format": "<the carousel format in 2-4 words: listicle, step-by-step, tips, story/narrative, side-by-side comparison, single graphic/quote, etc.>", "transcript": "<the full text content of every slide in order, verbatim and copy-pasteable; for a single image, its text>", "breakdown": "<ONE sentence: what the whole carousel actually is / its concept>", "why": "<1-2 sentences grounded in what's actually on the slides>"}`
>    Make sure it parses: escape inner quotes, no trailing commas, keep each value on one line. If the download failed, set "transcript" to "(unavailable)", "content_format" to "(unknown)", infer "hook"/"breakdown"/"why" from the caption, and still write the file.
> 4. Return ONLY one status line, nothing else:
>    `OK #<rank> @<handle> <Carousel|Image> | hook: <hook, ≤12 words> | why: <why, ≤18 words>`
>    (or `FAIL #<rank> @<handle> <Carousel|Image> | <one-line reason>` if the download failed.)

---

## PHASE 3 — Build the HTML Report & Open It (you, the orchestrator)

1. **Write the Pattern line.** From the returned status lines (hook + why per pick), write **3-4 short, punchy sentences MAX** on what repeats across the pool — lead with the takeaway, no preamble, scannable in ~5 seconds. Hit the highest-signal threads only (dominant hook archetype, the format/mechanic that recurs, the real engagement driver, the topic cycle, the biggest breakout). Don't catalog every post or quote every stat. Note any handle `rank-and-select.py` flagged as empty. Put it in **one `Write` call** to `<RUN_DIR>/pattern.txt` (plain text, no quotes-escaping needed). This becomes the report's "Pattern" block — keep it tight. (`<RUN_DIR>` is fresh per run, so there's never a stale `pattern.txt` to overwrite.)
2. **Assemble + render + open (ONE command).** Run:

   ```
   bash <SKILL_DIR>/scripts/build-report.sh "<RUN_DIR>" "<project_root>/research/IG-Competitor-Research_<RUN>.html" --open
   ```

   `build-report.sh` runs `build-report.py` on the shared build-once pillow venv (`~/.cache/content-os/pillow-venv`, built by uv on first use, sentinel-gated; `CONTENT_OS_PILLOW_VENV` overrides). Pointed at the **directory**, `build-report.py` assembles the manifest itself — `selection.json` is authoritative for the scraped + computed facts (rank, handle, format, likes, comments, date, url, breakout), each `<jobdir>/post.json` supplies the analysis, `pattern.txt` supplies the synthesis — then downscales + base64-embeds all media, writes the HTML (with breakout badges), leaves an inspectable `manifest.json` in `<RUN_DIR>`, and `--open` pops it in the browser. It prints the path and **warns on stderr if any pick was missing a usable `post.json`**.
3. **If a pick was flagged missing**, re-spawn just that one subagent (it re-writes its `post.json`), then re-run the build command. Otherwise you're done.
4. **Report the file path** back to the user — `research/IG-Competitor-Research_<RUN>.html` — plus the ranked table (with breakout) and the one-paragraph pattern.

RULES:
- The **hook is never the caption.** Reel hook = the host's first spoken line from the transcript (or the on-screen text hook if a text overlay carries the open); carousel/image hook = the slide-1 text. Each post also records `hook_type` (spoken / on-screen text / both), a 2-4 word `content_format` (talking head, listicle, side-by-side, reaction, …), a one-sentence `breakdown`, the full `transcript`, and `why`. The subagents capture all of this — don't override it.
- **Why it worked is grounded** in the real transcript + frames. One sharp mechanic beats a paragraph of praise. Never invent a view count or engagement rate.
- HTML is the only output. No markdown report. Scraped + computed facts always win over a subagent's echoed numbers (the builder enforces this).

---

## Rules of Thumb
- **ONE paid Apify call (start-and-return), then pull the dataset via the MCP.** Fire `call-actor` at `detailedData` with `waitSecs: 0` and poll `get-actor-run` (each poll with `waitSecs: 45`) until `SUCCEEDED` to get the `datasetId` — a blocking call can't outlast a multi-minute scrape anyway. That's the only paid step → `get-dataset-items` (same OAuth, no token) returns the items → you write them to `<RUN_DIR>/dataset.json` → `rank-and-select.py` does the rest. The dataset pull is MCP-only; never use an API token. No second scrape, no Chrome MCP, no Playwright.
- **Scripts own the mechanical work, you own the judgment.** You never sort posts, compute a score, format a date/like-count, write a `videourl.txt`, or hand-author a manifest. `rank-and-select.py` ranks + scores + preps; subagents write `post.json`; `build-report.py` assembles + renders. You only resolve handles, stamp the run, fire the scrape + pull the dataset, fan out, and write one Pattern line.
- **Default 5 handles, top 3 each.** 3 handles → 9 posts, 5 → 15. Order in `competitor-list.md` = priority. A handle with no posts in the window just contributes fewer (flagged by `--expect`).
- **Rank by likes; surface breakout.** Comments break ties. `-1` = hidden, sorted last. Breakout score = post likes ÷ that handle's weekly median (per-creator, robust to account size); a kept post with hidden likes shows `—`. All computed in `rank-and-select.py`, badged on every card.
- **Reels → `reel-breakdown.sh "<jobdir>" "$(cat <jobdir>/videourl.txt)"`** (curl the muxed `videoUrl` + ffmpeg keyframes + faster-whisper `small.en`). **Carousels/images → `fetch-images.sh "<jobdir>" "<jobdir>/imageurls.txt"`** (the script reads the URL file itself). Whisper override: `WHISPER_MODEL=medium.en`.
- **Why `detailedData` not `basicData`:** `basicData` omits the carousel slide array and the reel `videoUrl`, forcing a second paid scrape. `detailedData` hands back everything in one call. CDN URLs are signed + expire, so the subagents download immediately — the `videoUrl` is the only source, no fallback.
- **Subagents do the media, not you.** One Sonnet agent per pick, spawned in parallel; each writes `post.json` and returns a one-line status. Heavy video/image work stays out of the orchestrator context.
- **Claude reads the frames/slides directly** — no external vision provider.
- **Output is a self-contained HTML report** built by `build-report.sh` → `build-report.py` (Pillow downscales + base64-embeds every slide/frame — portable, no asset folder, no expiring links). Swipeable carousels, reel keyframe galleries, collapsible transcripts, breakout badges, "View on Instagram" buttons, 🔬 favicon. `--open` pops it in the browser.
- **Resilient assembly.** A pick whose `post.json` is missing/malformed still renders (media + facts + breakout), flagged on stderr — re-spawn that one subagent and re-run the build. Nothing else is lost.
- Input is locked: `dataDetailLevel: detailedData`, `onlyPostsNewerThan: "1 week"`, `resultsLimit: 20`, `skipPinnedPosts: true`. Pinned exclusion is handled by the actor.
- Intermediates (`dataset.json`, downloaded media, `selection.json`, `post.json`, `pattern.txt`, `manifest.json`) live in `<RUN_DIR>` = `/tmp/ig-research/<RUN>/` — timestamped, so every run is fully isolated: no collisions, nothing to clean. The HTML in `research/` is the durable artifact; each run writes its own `IG-Competitor-Research_<RUN>.html`.
