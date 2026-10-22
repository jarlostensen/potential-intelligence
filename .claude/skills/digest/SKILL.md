---
name: digest
description: Fetch and synthesize a digest of how technology organisations are adopting, adapting and learning with AI since the last run. Writes a dated entry to news/. Covers org structures and careers, engineering practice, product and adjacent disciplines, regulation and business risk, models and platforms, agent engineering, and tooling.
argument-hint: "[--since YYYY-MM-DD to override the auto-detected since date]"
allowed-tools: Bash, Write, Read, Glob, Edit, WebSearch, WebFetch, Agent, Artifact
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

### 1b — Annual and periodic reports

Several high-value sources publish as reports rather than feeds and will not appear in the fetch output. When the current month matches, search for the latest edition (web search or the publisher's page) and, if it was published since the last run, add it to the item set with `source` set to the publisher name:

| Report | Publisher | Typical month |
|---|---|---|
| Developer Survey | Stack Overflow | June–October |
| State of Developer Experience | Atlassian | September–October |
| State of AI-assisted Software Development (formerly Accelerate State of DevOps) | DORA / Google Cloud | September–October |
| State of Developer Ecosystem | JetBrains | July–September |
| Agentic Coding Trends Report | Anthropic | Variable |
| State of AI Impact in Engineering (quarterly) | DX | Quarterly |
| AI Index | Stanford HAI | April |
| Octoverse | GitHub | October–November |

Skip this sub-step silently when nothing new has been published.

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
- Is off-topic (not about how technology organisations use AI: engineering practice, org structure and careers, product and delivery, regulation and business risk, or the models, agents and tooling that drive those changes)
- Scores below 4.0 composite
- Duplicates a higher-scoring item already retained (keep the best-signal version)

## Step 4 — Assign tags, compute trends, write Overview

### 4a — Assign topic tags

For each retained item, assign 1–3 normalised topic tags. Use the top-50 vocabulary from Step 2 as the preferred tag set — introduce a new tag only when no existing tag is an adequate match. Keep new tags to a minimum and prefer broad labels over narrow ones (e.g. "MCP" not "MCP server discovery").

Tag format: short, title-case labels, e.g. "Claude Code", "MCP", "Memory", "RAG", "Local Inference", "Prompt Engineering", "Evaluation", "Fine-Tuning".

**First-class tags for the organisational focus** (introduced 22 Oct 2026; use these instead of folding everything into "AI Management"):

| Tag | Use for |
|---|---|
| Org Design | Team structures, reporting lines, roles, headcount and hiring changes, ways of working |
| Careers | Individual career impact, skills, junior pipeline, interviewing, compensation |
| Product Management | Product discovery, PRDs, roadmaps, product operating model, PM tooling |
| Delivery | Project and programme management, planning, estimation, release process |
| Regulation | Laws, enforcement, standards, compliance obligations (EU AI Act, FTC, export controls) |
| Business Risk | Vendor economics, pricing, liability, procurement, concentration risk, incidents with commercial consequences |
| AI Management | Reserve for leadership strategy and governance that does not fit a narrower tag above |

Existing tags (Agent Engineering, AI-Assisted Dev, Evaluation, Security, LLM Models, Local Inference, Tools, Performance, Cloud Infrastructure, Context Management, Multi-Agent, Claude Code, Anthropic, MCP, Memory, MLOps, Knowledge Graph, RAG, Prompt Engineering) remain valid.

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

1. **Organisations, Roles and Careers** — how companies restructure around AI, hiring and the junior pipeline, role changes, internal adoption data, employee experience
2. **Engineering Practice and Delivery** — coding workflows, code review, testing and verification, source control and CI at agent scale, developer-experience research, harness and workflow patterns teams actually adopt
3. **Product, Project and Adjacent Disciplines** — product management, project and programme management, design, data, support and other functions adopting AI; internal tooling for non-engineers
4. **Regulation, Risk and Governance** — laws and enforcement, standards and certification, liability, vendor economics and pricing, procurement constraints, incidents with business consequences
5. **Models and Platforms** — model releases and benchmarks from any lab (including Claude and Anthropic), pricing changes, capability shifts that change what organisations can do
6. **Agent Engineering** — multi-agent patterns, orchestration, memory, context management, tool use, evaluation of agents
7. **Tools and Infrastructure** — new or significantly updated tools, inference and cloud infrastructure, local inference, systems-level performance

Within each section, order by composite score descending. Sections 1–4 are the digest's centre of gravity; when an item fits both a practice section and a models or tools section, place it in the practice section.

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

## Step 9 — Write, publish, and post the Slack summary

Write a condensed Slack message, publish it as a Claude Artifact with a one-click copy button (9a–9c), then post it automatically to the configured Slack channel (9d).

The digest itself is not capped; the Slack summary is. It is a short pointer to the digest, not a second digest.

### 9a — Compose the message text

Use only Unicode characters and emoji — no Slack markdown (`*bold*`, `_italic_`). The message must look clean as raw text before it is posted.

**Selection rules for the Slack summary (22 Oct 2026):**
- Exclude every item from the **Models and Platforms** section from the Slack summary entirely, including the headline. They remain in the digest.
- The HEADLINE is the highest-scoring retained item from any other section.
- TOP PICKS holds **at most 4 items**, ordered by signal descending, drawn from sections 1–4 first; include an Agent Engineering or Tools item only if fewer than 4 items from sections 1–4 score above 6.0.
- Each pick body is **one or two sentences**; the headline paragraph is at most three.
- TREND is at most two sentences.
- Target length: under 2,500 characters.

**Structure** (use this exact skeleton):

```
🔬  AI Tool Digest  ·  {D Month YYYY}

Coverage: {since date D Mon} → {fetched date D Mon}  ·  {item_count} items from {total fetched} fetched

────────────────────────────────────────

📈  HEADLINE

{Title of the single highest-scoring retained item. One short paragraph: what it is, why it matters, one concrete implication. 3–4 sentences max.}
{full https:// URL on its own line}

────────────────────────────────────────

TOP PICKS

{emoji}  {Title}  ·  {N}K ★   ← include star count only for GitHub items
{2 sentences: what it is and what a practitioner should do with it.}
{full https:// URL on its own line}

{repeat for up to 3 more items, ordered by signal score descending; never from Models and Platforms}

────────────────────────────────────────

📌  TREND

{2–3 sentences. Which tags are rising or resurfaced. Which tags are notably absent this run compared to recent history.}
```

Rules:
- The `────────────────────────────────────────` divider is exactly 40 `─` characters.
- Omit the HEADLINE item from TOP PICKS (it is already covered).
- TOP PICKS: include up to 4 items total (excluding the headline), following the selection rules above. If fewer than 4 qualify, include only those.
- Star counts: round to one decimal and append K (e.g. `53K ★`, `223K ★`). Omit for non-GitHub items.
- URLs: always full `https://` so Slack auto-links them. One URL per item, on its own line immediately after the item text.
- No trailing blank lines inside item blocks.

**Emoji selection by primary tag** (pick the best fit; use the first match):

| Tag | Emoji |
|---|---|
| Org Design / Careers | 🏢 |
| Product Management / Delivery | 🧭 |
| Regulation | 🏛️ |
| Business Risk | 💼 |
| Security | 🔒 |
| Evaluation / MLOps | 📊 |
| Agent Engineering (loop/control) | 🔁 |
| Agent Engineering (harness/framework) | 🔧 |
| Context Management / Performance | ⚡ |
| Memory | 💾 |
| AI-Assisted Dev / Claude Code | 🛠️ |
| LLM Models / Anthropic | 🌐 |
| Prompt Engineering | 🧠 |
| Cloud Infrastructure | ☁️ |
| Growth metric / adoption data | 📈 |
| Policy / regulatory | 🏛️ |
| Incident / failure analysis | 💥 |
| Anything else | 🔹 |

### 9b — Write the HTML artifact file

Write a self-contained HTML file to the session scratchpad at:
`{scratchpad}/slack-digest.html`

The file must contain:
1. A read-only monospace preview pane showing the exact message text from 9a.
2. A single "Copy message" button. On click: copies the text to the clipboard, changes its label to "Copied ✓" for 2 seconds, then resets.
3. A one-line note below the button: `URLs auto-link in Slack. Separator lines and emoji render correctly on desktop and mobile Slack.`

**CSS spec** (derive all colours from these tokens):
- `--bg: #0f1117` — page background
- `--surface: #161b27` — preview pane background
- `--border: #252d3d` — preview pane border
- `--text: #cbd5e1` — preview pane text
- `--dim: #64748b` — label and note colour
- `--green: #34d399` — copy button border and text (transparent background, fills on hover)
- Font for preview pane: `'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,monospace`
- Preview pane: `white-space: pre-wrap`, `word-break: break-word`, `font-size: 0.82rem`, `line-height: 1.75`
- Page layout: single column, centred, max-width 680px
- A small ALL-CAPS dim label above the preview reading `Slack message · Run {N} · {D Month YYYY}`

### 9c — Publish as Artifact

Call the Artifact tool:
- `file_path`: the scratchpad path from 9b
- `favicon`: `📋`
- `label`: `slack-{DD}{mon}` (e.g. `slack-29jun`)

### 9d — Post to the Slack channel

Write the exact message text from 9a to a UTF-8 file in the scratchpad (e.g. `{scratchpad}/slack-message.txt`) — write it verbatim, identical to what the artifact preview shows. Then run the posting script from the project root:

```
uv run scripts/post_to_slack.py --message-file {scratchpad}/slack-message.txt
```

The script chooses its delivery mechanism automatically from credentials in the environment or the project-root `.env` file (see **Slack configuration** below):

- **Bot token** — used when `SLACK_BOT_TOKEN` and a channel are set (`SLACK_CHANNEL`, or pass `--channel "#name"`). Posts via `chat.postMessage`.
- **Incoming webhook** — used when only `SLACK_WEBHOOK_URL` is set. Posts to that webhook's fixed channel.
- **Skip** — if neither is configured, the script prints a warning and exits 0. This is expected and NOT a failure: the artifact from 9c still stands. Do not treat a skip as an error.

Interpret the result:
- Exit 0 with `"delivered": true` on stdout → posted. Report the channel/method in the run summary.
- Exit 0 with `"delivered": false, "reason": "not_configured"` → skipped; tell the user Slack posting is not yet configured and point them at **Slack configuration**.
- Exit 1 → a delivery was attempted and failed. Report the stderr message (common causes: `not_in_channel` → invite the bot to the channel; `invalid_auth`/`missing_scope` → token needs `chat:write`; webhook HTTP error). The artifact still stands.

Add `--dry-run` to validate configuration without posting.

Report the artifact URL AND the Slack post outcome (posted to which channel, skipped, or failed) to the user alongside the run summary.

### Slack configuration (one-time setup)

Credentials live in a gitignored `.env` file at the project root (`.env` and `*_api_key*` are already in `.gitignore`). Never commit them. Choose one:

**Option A — Incoming webhook (simplest, one fixed channel):**
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/xxxxxxxxxxxxxxxx
```
Create at api.slack.com → your app → *Incoming Webhooks* → *Add New Webhook to Workspace*, selecting the target channel.

**Option B — Bot token (flexible channel, threading):**
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL=#ai-digest
```
Create a Slack app with the `chat:write` bot scope, install it to the workspace, and invite the bot to the channel (`/invite @your-bot`). If both a bot token and a webhook are present, the bot token wins.

Real environment variables take precedence over `.env`, so CI/cron can inject credentials without a file.
