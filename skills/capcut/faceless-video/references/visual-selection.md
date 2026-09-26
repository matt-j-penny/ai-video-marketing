# Visual selection — writing shots.json

Input: `words.json` (every spoken word with start/end seconds) and `script.md`.
Output: `shots.json`, one entry per image on screen.

```json
{
  "shots": [
    {"start": 0.0,  "anchor": "Colosseum", "prompt": "The Colosseum at dawn, seen from street level, ..."},
    {"start": 2.31, "anchor": "50,000",    "prompt": "A packed arena crowd ..."}
  ]
}
```

- `start`: the `start` of the anchor word in `words.json`, copied exactly. The first shot is always `0.0`. You don't write `end`: each shot runs until the next one starts, and the last one runs to the end of the voiceover.
- `anchor`: the word/phrase the cut lands on. For review only.
- `prompt`: the subject and composition only. The style block is appended automatically; don't repeat style words here.
- `motion` (video mode only, optional): how the shot should move ("slow push in, smoke drifting").

## Shot spacing (from the `cut_speed` preference)

| cut_speed | target seconds per shot | hard limits |
|---|---|---|
| fast | ~2 | 1.2–3.5 |
| medium | ~3.5 | 2–5 |
| slow | ~5 | 3–8 |

So a 60s fast video has roughly 25–30 shots. Never go over the hard max, even if the next strong anchor is further away; in that case pick the best available noun in between.

## What earns a cut (in priority order)

1. **Concrete, picturable nouns.** People, places, objects, animals, events: "Cleopatra", "a gold coin", "the Titanic's boiler room". Best anchors by far.
2. **Numbers and scale.** "50,000 people", "3 kilometres down". Show the scale, not the digit.
3. **Turns in the story.** "But then", "Until", "Instead", the new thing after the turn gets the cut.
4. **Actions with a visual verb.** "collapsed", "flooded", "exploded".

Cut **on** the anchor word (its start time), so the image lands as the word is spoken.

## What does NOT earn a cut

- Filler and connective words (so, and, actually, really, just, this).
- Abstract words with nothing to picture (importance, idea, reason, concept). If a sentence is all abstraction, show the concrete subject the sentence is *about*.
- Pronouns. Show what "it" refers to.
- The same subject twice in a row with the same framing. If the script stays on one subject, vary the shot: wide → close-up → detail → different angle.

## Writing each prompt

- One clear subject, one clear composition. "Close-up of a Roman soldier's bronze helmet on a wooden table, side light".
- Say the framing: wide / medium / close-up / overhead / detail.
- Must be literally what's being said at that moment, specific to the topic. Never generic stock imagery ("a person thinking", "abstract technology background").
- No text, logos, captions, or UI inside the image. Captions are added in CapCut.
- Keep people's identities generic unless the topic is a real, famous historical figure.
- Leave the lower third of the frame visually quiet (sky, floor, shadow) where the caption sits.

## Self-check before showing shots.json

- First shot at 0.0; starts strictly increasing; every `start` matches a real word's start in `words.json`.
- Gaps between consecutive starts within the cut_speed hard limits (the final shot included: last start → voiceover end).
- No two adjacent prompts with the same subject and framing.
