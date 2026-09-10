# Corpus tag vocabulary

Every entry in `voice-corpus/` carries four tags in its frontmatter. `find_voice.py`
(the scriptwriter's retrieval) filters on them, so **use these exact values** — a
misspelled tag makes the entry invisible to the format filter.

## `format` — what kind of video it is (structure, not topic)

| tag | means |
|---|---|
| `giveaway-demo` | Shows a system/asset working, then gives it away for a comment keyword / link. The default short-form shape for most creators who sell. |
| `tutorial-walkthrough` | Teaches steps on screen (numbered or chained), viewer does it themselves. |
| `case-study` | A client / member / own result told as before → after → what made the difference. |
| `transparency` | Raw money / numbers / behind-the-scenes talk, usually no demo. |
| `build-in-public` | Shows the finished artifact first, then builds or runs it live. |
| `rant` | Opinion-driven take, little or no demo. |
| `story` | Narrative arc (origin story, "how I…"), story is the vehicle. |
| `listicle` | "N things / tools / mistakes" — enumerated items are the structure. |
| `reaction` | Reacts to a clip / post / news item. |
| `vlog` | Day-in-the-life / journey footage. |
| `interview` | Two-person conversation as the format. |
| `other` | Nothing above fits (rare — prefer the closest one). |

## `hook_type` — the mechanic of the FIRST spoken sentence

| tag | means | example shape |
|---|---|---|
| `bold-claim` | First-person completed result with a number/timeframe. | "I just cut my grocery bill in half with one spreadsheet." |
| `question` | Direct question at the viewer's behavior or pain. | "Are you still stretching before you lift?" |
| `callout` | Attacks the viewer's current behavior, pledges the fix. | "This is how most of you write your bio. That's terrible." |
| `secret-reveal` | Promises a hidden thing, proof follows in sentence two. | "I'm about to give away the template I charge for." |
| `shock-number` | Leads with one startling stat. | "A new study says 49% of people never finish the course they bought." |
| `contrarian` | Flips a common belief. | "You don't need a niche." |
| `how-to` | Names the outcome + method up front. | "Here's how to plan a month of posts in 30 minutes." |
| `story-open` | Opens mid-story. | "Last Tuesday a client sent me this…" |
| `title` | Long-form only: the YouTube TITLE is the hook (spoken open is a proof stack). |
| `other` | Nothing above fits. |

## `era`

Free-form, one word. `current` = the voice + niche to write in by default. If the
creator pivoted (old niche, old offer), tag that older content with a second word
(e.g. `previous`) so scriptwriter can prefer `current` and reach back only when a
format has no current example.

## `spoken_hook`

The first spoken sentence, **verbatim** from the transcript (short-form). Long-form:
the video title. Never the caption, never on-screen text.
