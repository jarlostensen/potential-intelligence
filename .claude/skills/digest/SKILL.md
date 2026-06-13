---
name: digest
description: Fetch and synthesize a digest of current AI tool trends and practices since the last run. Writes a dated entry to news/. Covers Claude, LLMs, agent engineering, AI-assisted software development, cloud, and systems engineering.
argument-hint: "[--since YYYY-MM-DD to override the auto-detected since date]"
allowed-tools: Bash, Write, Read, Glob
---

# AI Tool Digest

Generate a digest of current AI tool trends from free public sources and synthesize the findings.

## Step 1 — Fetch raw content

Run the fetch script from the project root:

```
uv run scripts/fetch_digest.py $ARGUMENTS
```

Progress messages go to stderr (visible in the terminal). JSON output goes to stdout and is what you will process.

If `uv` is not found or the script exits with an error, report the failure and stop — do not attempt to proceed without data.

## Step 2 — Load the signal ledger

Read `data/signal-ledger.json` if it exists.

**On any failure, continue without trend history:**
- File does not exist → treat as empty ledger (no prior runs), no warning needed
- File exists but is not valid JSON → emit "Warning: signal ledger is malformed — ignoring and continuing without trend history." Do not abort.
- File exists, valid JSON, but `version` field is not `1` → emit "Warning: signal ledger has unknown schema version — ignoring and continuing without trend history." Do not abort.
- File exists and valid → extract the `runs` array

From the runs array, build two things for use in later steps:

1. **Tag vocabulary**: all tags ever used across all runs, sorted by lifetime frequency (count of runs in which the tag appeared). Pass the top 50 as context when assigning tags in Step 4. This prevents near-synonym drift.

2. **Run count**: the total number of prior runs. If fewer than 3, note that the Trend Summary will be skipped. If 3–6, note that the Trend Summary will be labelled provisional.

## Step 3 — Apply the signal ranking framework

The script outputs a JSON object. The `items` array contains every fetched item with fields: `title`, `url`, `date`, `source`, `score` (upvotes or stars), `comments`, `snippet`.

Score each item using the framework from CLAUDE.md:

| Dimension | Weight | Question |
|---|---|---|
| Impact | 0.35 | Does this meaningfully improve outcomes for expert practitioners? |
| Novelty | 0.20 | Is this genuinely new, or a restatement of established practice? |
| Adoption Velocity | 0.20 | Are expert practitioners actively moving toward this? |
| Repeatability | 0.15 | Can others reproduce the result with reasonable effort? |
| Generality | 0.10 | Does this apply broadly, or only in narrow conditions? |

Composite = Impact×0.35 + Novelty×0.20 + AdoptionVelocity×0.20 + Repeatability×0.15 + Generality×0.10

**Discard** any item that:
- Is primarily a product announcement with no demonstrated technique
- Lacks reproducible evidence (anecdotes only)
- Is off-topic (not AI tools, software engineering, cloud, or client/systems infrastructure)
- Scores below 4.0 composite
- Duplicates a higher-scoring item already retained (keep the best-signal version)

## Step 4 — Assign tags, compute trends, write Overview

### 4a — Assign topic tags

For each retained item, assign 1–3 normalised topic tags. Use the top-50 vocabulary from Step 2 as the preferred tag set — introduce a new tag only when no existing tag is an adequate match. Keep new tags to a minimum and prefer broad labels over narrow ones (e.g. "MCP" not "MCP server discovery").

Tag format: short, title-case labels, e.g. "Claude Code", "MCP", "agent memory", "RAG", "local inference", "prompt engineering", "evaluation", "fine-tuning".

### 4b — Compute trend classifications

For each tag that appears in the retained items, compute appearance rates from the prior runs loaded in Step 2:

- **Recent rate**: fraction of the last 7 runs in which the tag appeared
- **Baseline rate**: fraction of the last 30 runs in which the tag appeared

Classify each tag:

| Classification | Condition |
|---|---|
| New | Fewer than 3 lifetime appearances in the ledger |
| Rising | Recent rate > baseline rate by 0.20 or more |
| Steady | Recent and baseline rates within 0.15 of each other |
| Cooling | Recent rate < baseline rate by 0.20 or more |
| Resurfaced | Absent from the most recent 7 runs, now reappears |

When fewer than 3 prior runs exist, skip the Trend Summary entirely. When 3–6 prior runs exist, include the Trend Summary but add a note: "_Provisional — based on fewer than 7 prior runs._"

### 4c — Write the Overview paragraph

3–5 sentences. What domains or topics dominate this digest? Any standout high-signal items? What is notably absent that appeared in recent runs?

## Step 5 — Group and synthesise

Group surviving items into these sections. Omit any section with no qualifying items:

1. **Claude and Anthropic** — model updates, Claude Code, MCP, API changes, Anthropic research
2. **LLM Models and Capabilities** — other notable models, benchmark results, emergent capabilities
3. **Agent Engineering** — multi-agent patterns, orchestration, memory systems, tool use
4. **AI-Assisted Software Development** — coding workflows, spec-driven dev, AI code review, prompt patterns
5. **Cloud and Infrastructure** — cloud-native AI deployment, MLOps, inference serving, GitOps
6. **Client and Systems Engineering** — native/C++ tooling, build systems, performance, embedded AI
7. **Tools and Frameworks** — new or significantly updated tools worth tracking

Within each section, order by composite score descending.

## Step 6 — Write the digest

Determine today's date and current time for the filename: `news/YYYY-MM-DD-HHMM.md`

Create the `news/` directory if it does not exist.

Write the file using this exact structure:

```
---
date: {ISO 8601 with UTC offset, e.g. 2026-05-31T14:30:00+00:00}
since: {since cutoff from the JSON fetched_at field}
sources:
  - {each source name that contributed at least one retained item}
item_count: {count of items in the digest, excluding the excluded table}
top_tags:
  - {tag name}
  - {tag name}
---

# AI Tool Digest — {D Month YYYY}

_Coverage: {since date formatted as D Month YYYY} to {fetched_at date formatted as D Month YYYY}_

## Overview

{3-5 sentences from Step 4c}

## Trend Summary

**Rising**: {tag, tag, tag}
**New this period**: {tag, tag}
**Steady**: {tag, tag, tag}
**Cooling**: {tag, tag}
**Resurfaced**: {tag, tag}

_Based on {N} prior runs. Trend window: recent = last 7 runs, baseline = last 30 runs._

(Omit the Trend Summary section entirely when fewer than 3 prior runs exist.
Add "_Provisional — based on fewer than 7 prior runs._" when 3–6 prior runs exist.)

## {Section heading}

### {Item title}
**Source**: {source} | **Date**: {D Mon YYYY} | **Signal**: {composite score to 1 decimal place} | **Tags**: {tag, tag}

{2-4 sentences. State what this is, why it matters to a senior software engineer or architect, and what concrete action or change in practice it suggests.}

[Source]({url})

---
{blank line between items}

## Excluded items

| Title | Source | Reason |
|---|---|---|
| {truncated title, max 60 chars} | {source} | {one-line reason} |
```

`top_tags` in the front matter: list of tag strings for the top 5 tags by item count in this digest, ordered by frequency descending.

## Step 7 — Update the signal ledger

Read the current contents of `data/signal-ledger.json` again (or start with `{"version": 1, "runs": []}` if it does not exist or was unreadable in Step 2).

Build the new run record:

```json
{
  "date": "{ISO 8601 timestamp of this run}",
  "digest_file": "news/{filename}.md",
  "item_count": {count of retained items},
  "topics": [
    {
      "tag": "{tag name}",
      "count": {number of retained items with this tag},
      "avg_signal": {average composite score of items with this tag, 1 decimal},
      "cluster_id": null
    }
  ]
}
```

Append this record to the `runs` array to produce the complete updated ledger document.

**Write the complete ledger document** (not an append — write the full JSON from `{"version": 1, ...}` to the closing `}`) to `data/signal-ledger.json` using the Write tool. Writing the complete document means a partial-write failure leaves either the old file intact or the new file complete — never a hybrid.

Create the `data/` directory if it does not exist.

After writing, report the output path and the count of items included. If the ledger was unreadable in Step 2, note that trend history has been reset.

## Step 8 — Write news/latest.html

Write a self-contained HTML rendering of this digest to `news/latest.html`. This file is always overwritten so it always reflects the most recent run. Use the Write tool.

### Requirements

**Self-contained** — all CSS must be in a `<style>` block in `<head>`. No external scripts, no CDN links, no web fonts. The file must render correctly when opened directly from the filesystem (`file:///`).

**All links** open in `target="_blank" rel="noopener"`.

### Page structure

```
<header>
  <h1>AI Tool Digest</h1>
  <p class="meta">{D Month YYYY} · {item_count} items · Coverage: {since date} → {fetched_at date}</p>
  [Trend Summary pill row if present]
</header>

<main>
  [One <section> per digest section heading]
  [Each item as an <article> with title, meta bar, body, source link]
  [Excluded items as a <details><summary> collapsed table at the bottom]
</main>
```

### Item card structure

```html
<article>
  <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
  <p class="item-meta">
    <span class="signal">{score}</span>
    <span class="source">{source}</span>
    <span class="date">{date}</span>
    {tags rendered as <span class="tag">…</span> chips}
  </p>
  <p>{body text}</p>
</article>
```

### Trend Summary (if present)

Render each classification (**Rising**, **New this period**, **Steady**, **Cooling**, **Resurfaced**) as a row of coloured pill chips inside the header. Omit entirely if the Trend Summary was skipped for this run.

### CSS guidance

- Background: `#0f1117`, text: `#e2e8f0` (dark theme)
- Max content width: 860px, centred
- Section headings: left-bordered accent (`border-left: 3px solid #7c3aed`)
- Signal score chip: bold, monospace, background `#1e293b`, colour varies by range:
  - ≥ 7.5: `#34d399` (green)
  - 6.5–7.4: `#60a5fa` (blue)
  - < 6.5: `#94a3b8` (muted)
- Tag chips: `background: #1e293b`, `color: #a78bfa`, small font
- Trend pills: Rising `#34d399`, New `#60a5fa`, Steady `#94a3b8`, Cooling `#f59e0b`, Resurfaced `#f472b6`
- Article cards: subtle border `#1e293b`, `border-radius: 6px`, padding, bottom margin
- Source link: muted, small, no underline until hover
- Excluded items `<details>` styled as collapsible, closed by default
