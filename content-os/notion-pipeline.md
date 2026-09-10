# Notion Content Pipeline — Schema Reference

Live schema for YOUR Notion content database. **Pure reference, no execution logic.** Any skill
that reads or writes the pipeline (scriptwriter, yt-description, the status-sync rules in
CLAUDE.md) loads this file for IDs and property shapes.

> Status: **<<NOTION_STATUS: "not created yet" until "apply my brand kit" creates the DB and fills the Identity table below>>**

---

## Identity

| Field | Value |
|-------|-------|
| **Database name** | <<NOTION_DB_NAME: e.g. "Content Pipeline">> |
| **Database ID** | `<<NOTION_DB_ID>>` |
| **Data source ID** | `<<NOTION_DATA_SOURCE_ID>>` (differs from the DB ID; the parent for `notion-create-pages`, and the search scope as `data_source_url: collection://<<NOTION_DATA_SOURCE_ID>>`) |
| **Parent page** | <<NOTION_PARENT_PAGE: the page the DB lives under>> (`<<NOTION_PARENT_PAGE_ID>>`) |
| **URL** | <<NOTION_DB_URL>> |

### Creating it (Claude does this during "apply my brand kit")

One call to the Notion MCP tool `notion-create-database` under a parent page of the user's choice
(ask for the page in one line if brand-kit.md left it blank), with exactly the properties below;
then `notion-fetch` the new database, copy the Database ID, Data source ID, and URL into the table
above, and replace the status line. Views (Board grouped by Status, Calendar by Post Date) can be
added with `notion-create-view`; they're nice, not required.

---

## Properties

| Name | Type | Notes |
|------|------|-------|
| **Title** | `title` | Page title (the working title of the video) |
| **Status** | `status` | Pipeline stage, see flow below. Options: Idea, Scripting, To Edit, Editing, Review, Ready, Posted, Archived |
| **Format** | `select` | `Short-form` · `Long-form` |
| **Type** | `multi_select` | Funnel placement, tagged by the creator by hand: `TOF` · `MOF` · `BOF` (skills never set this) |
| **Post Date** | `date` | YYYY-MM-DD, set when status flips to Posted |
| **Source URL** | `url` | The source video being recreated/twisted (the format model). Set on twist picks at scripting time. |
| **Raw Footage** | `url` | Link to the raw clips (Drive, Frame.io, etc). Filled after filming, not on script creation. |
| **Edited Video** | `url` | Link to the final edit |
| **Created time** | `created_time` | Auto |
| **Last edited time** | `last_edited_time` | Auto; use for staleness checks |

---

## Status flow

```
Idea → Scripting → To Edit → Editing → Review → Ready → Posted → Archived
```

| Group | Statuses |
|-------|----------|
| **To-do** | Idea |
| **In progress** | Scripting, To Edit, Editing, Review, Ready |
| **Complete** | Posted, Archived |

`Ready` is the handoff stage: the edit is done and approved, waiting to publish. Posting goes
through the `auto-poster` skill (Zernio), which takes a video path/URL directly and does **not**
read Notion itself; the session that ran it flips `Ready → Posted` and sets `Post Date` right after
a successful post (standing rule in CLAUDE.md, "Videos live in Notion"). There is intentionally no
"Scheduled" status.

---

## Property write shapes

The MCP `notion-create-pages` / `notion-update-page` tools take a flat property map keyed by the
property NAME (`{"Title": "...", "Status": "Scripting", "Format": "Short-form", "Source URL": "https://..."}`),
plus markdown `content` for the page body. Set an emoji icon on every create (📦 for videos).
Leave `Type` blank; the creator tags funnel placement by hand.

---

## Reading and writing (Notion MCP only, no CLI, no token)

- **Resolve a video by name → `notion-search`** with one distinctive keyword from the title and
  `data_source_url` = `collection://<Data source ID>` (the data source, not the database), then `notion-fetch` the hit for its status
  and body. Title matching is fuzzy: users won't type exact titles; if several pages plausibly match,
  list them and ask.
- **Create → `notion-create-pages`** with the Data source ID as the parent (NOT the Database ID).
- **Update status / dates → `notion-update-page`.**
- **Pagination:** any list path caps at 100 results; check `has_more` and continue until exhausted.

---

## When to update this file

Re-fetch and rewrite whenever a property is added/renamed or its options change, a status is added,
or the database is moved/recreated. Quick re-verify: "Re-fetch the content DB with `notion-fetch`
(the Database ID above) and diff against `notion-pipeline.md`."
