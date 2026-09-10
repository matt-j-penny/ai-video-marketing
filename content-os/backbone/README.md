# backbone/ — your business, the single source of truth

Four short files every skill reads before it writes anything for you: who you are
(`vision.md`), what you sell (`offer.md`), who it's for (`icp.md`), and how you talk
about it (`messaging.md`). Scripts, hooks, carousels, captions, DMs, and YouTube
descriptions all pull the offer name, price, CTA, proof, and positioning from HERE, so
nothing is ever hardcoded in a skill.

**How it gets filled:** you fill in `brand-kit.md` at the project root and tell Claude
**"apply my brand kit"**. Claude writes these four files from it (and keeps the
`<<placeholder>>` tokens only where you left something blank). You can also just edit
them by hand; keep the section headers.

Rules that keep this useful:
- Status headers carry a date ("Current as of YYYY-MM-DD"), never "locked".
- Numbers (followers, revenue, members) go stale fast: refresh them here, never restate
  them inside skills or CLAUDE.md.
- When positioning or price changes, update these files THE SAME DAY.
