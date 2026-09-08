---
name: create-design-md
description: "Create a DESIGN.md file — a plain-text design system document that captures a product's or brand's complete visual language (colors, type, components, spacing, elevation, and rules) so a video editing or motion graphics workflow generates title cards, lower-thirds, overlays, and UI mockups that look consistent with it. Use when the user wants to document an existing app/website's design system, extract design tokens from a URL, CSS, or a Tailwind/theme config, or build a brand-new design system from scratch through a guided set of questions when there's no reference material to work from."
metadata:
  version: 1.0.0
---

# Create a DESIGN.md

A DESIGN.md puts a product's visual identity into words precise enough for an AI agent to build matching visuals — motion graphics, title cards, lower-thirds, UI mockups inside a video — without ever seeing a screenshot: exact colors, exact type sizes, exact spacing, exact component states, plus enough prose that the *feel* comes through, not just the numbers.

## Step 1: Figure Out the Source

Work out which of these applies before drafting anything:

1. **A live site or app** — the user gives a URL. Fetch it and read computed styles, CSS, and visual structure directly rather than guessing.
2. **Existing code** — CSS files, a Tailwind config, a theme object, or design tokens already sitting in the user's repo. Read them directly.
3. **A reference brand/mood** — the user names a brand or aesthetic they want the new system to feel like (not copy exactly).
4. **Nothing at all** — no URL, no code, no clear reference. Don't guess or invent one silently — run the question set below.

## Step 2: No Reference Material? Ask.

When there's genuinely nothing to extract from, build the system by asking a short, ordered set of questions rather than presenting a single design and hoping it lands. Ask them together as one set, not one at a time over ten round-trips, and offer sensible examples in each so the user can answer quickly:

1. **What is this?** — product/brand name, one sentence on what it does and who it's for.
2. **What should it feel like?** — 2-3 adjectives (e.g. "calm and trustworthy" vs "bold and energetic" vs "playful and warm" vs "precise and technical"). If they're stuck, offer 4-5 adjective pairs to pick from.
3. **Light, dark, or both?**
4. **Any color to anchor on?** — one hex code, a brand color, or "fully open, you choose."
5. **Type character** — serif or sans; geometric/clean or humanist/warm; editorial or functional.
6. **Density** — compact and information-dense, or generous and spacious.
7. **Shape language** — sharp corners, softly rounded, or pill-shaped/very round.
8. **Reference points** — any existing products/brands whose *feel* (not exact look) they'd want this to sit near.
9. **Where does it live?** — a marketing video's on-screen graphics, a web app/dashboard being demoed, a mobile app — this changes which components and what density actually matter.

Don't skip to writing after just the first couple of answers — a system built on "calm and trustworthy" alone still needs the type/density/shape answers to be specific rather than generic.

## Step 3: Calibrate Against a Real Example (when extracting)

If well-written design-system docs already exist elsewhere in the user's project or environment, skim one before drafting, purely to match the level of specificity expected — exact hex values, exact pixel sizes, named component states — rather than vague description. If none are available, hold the draft to the standard implied by the checklist in Step 5.

## Step 4: Draft the Sections

Every DESIGN.md needs to cover these, in order:

1. **Visual Theme & Atmosphere** — prose, not specs. What the design feels like and why: mood, density, typography personality, color story. Close with 6-10 bullet points naming the specific, concrete traits that produce that feel — not "clean and modern," but the actual choice that makes it read that way.
2. **Color Palette & Roles** — every color used, with its hex value and what it's *for*, grouped by role: primary/brand, interactive (links, CTAs, hover, focus), text hierarchy (heading/body/secondary/muted/disabled), surfaces & borders, shadows, and status colors (success/warning/error) if any exist.
3. **Typography** — font families with fallback stacks, then a complete size/weight/line-height/letter-spacing table covering at minimum: display, heading, subheading, body, button, caption, and micro-text.
4. **Components** — buttons (every variant × every state: default/hover/active/disabled/focus), cards/containers, form inputs (including the error state), navigation, plus anything visually distinctive to this design specifically.
5. **Layout & Spacing** — the base spacing unit and its scale, grid/container widths and gutters, whitespace philosophy, and the corner-radius scale.
6. **Depth & Elevation** — shadow values for each elevation level, how surfaces stack, and any special depth treatment (glass, gradients, overlays).
7. **Do's and Don'ts** — five or more of each. These are the rules that keep the system's identity intact under pressure — write them specific to this design, not generic design advice.
8. **Responsive Behavior** — breakpoints with actual pixel values, touch-target minimums, how layout collapses, how type scales down.
9. **Agent Prompt Guide** — a short cheat-sheet at the end: the 5-6 colors used most, 3-4 example prompts showing how to ask an agent to build a component (or a motion graphic, title card, lower-third) in this system, and common follow-up adjustments.

Every section needs actual values — a color role with no hex code, or a type row with no pixel size, isn't finished yet.

## Step 5: Validate Before Writing

- [ ] Section 1 ends with concrete, specific bullet traits, not adjectives alone
- [ ] Every named color has a hex value and a stated role
- [ ] The typography table has every column filled for every row
- [ ] Buttons cover every state, not just default
- [ ] The spacing scale has actual numbers, not "small/medium/large"
- [ ] Shadows have real rgba/hex values per elevation level
- [ ] Do's/Don'ts are specific to this design, not generic UI advice
- [ ] Breakpoints have real pixel values
- [ ] The agent prompt guide has runnable example prompts, not placeholders

If something in the draft is still vague, don't ship it — extract the real value from the source, or, if none exists, go back and ask.

## Step 6: Write the File

Save as `DESIGN.md`, in the location the user specifies — default to the project root if they don't say. Open with a first line naming what the file documents, e.g. `# Design System — {Name}`.

## Common Mistakes

1. Writing vague prose ("clean, modern, minimal") in place of the actual hex/pixel values that make a system usable by an agent.
2. Skipping the question set when there's no reference material and inventing a design without checking it matches what the user actually wants.
3. Asking one question at a time instead of the whole set together — burns the user's time across many round-trips.
4. Leaving a component's states (hover/active/disabled) undocumented — an agent building from this file will guess, and guess wrong.
5. Treating "Do's and Don'ts" as generic design advice instead of guardrails specific to this particular system's identity.

## Task-Specific Questions

1. Is this documenting something that already exists (a live site, existing code) or designing something new from scratch?
2. Where should the finished `DESIGN.md` be saved?
3. Any non-negotiables already decided (a locked brand color, an existing type system) that the rest of the system needs to build around?
