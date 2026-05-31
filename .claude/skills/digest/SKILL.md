---
name: digest
description: Fetch and synthesize a digest of current AI tool trends and practices since the last run. Writes a dated entry to news/. Covers Claude, LLMs, agent engineering, AI-assisted software development, cloud, and systems engineering.
argument-hint: "[--since YYYY-MM-DD to override the auto-detected since date]"
allowed-tools: Bash, Write, Glob
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

## Step 2 — Apply the signal ranking framework

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

## Step 3 — Group and synthesise

Group surviving items into these sections. Omit any section with no qualifying items:

1. **Claude and Anthropic** — model updates, Claude Code, MCP, API changes, Anthropic research
2. **LLM Models and Capabilities** — other notable models, benchmark results, emergent capabilities
3. **Agent Engineering** — multi-agent patterns, orchestration, memory systems, tool use
4. **AI-Assisted Software Development** — coding workflows, spec-driven dev, AI code review, prompt patterns
5. **Cloud and Infrastructure** — cloud-native AI deployment, MLOps, inference serving, GitOps
6. **Client and Systems Engineering** — native/C++ tooling, build systems, performance, embedded AI
7. **Tools and Frameworks** — new or significantly updated tools worth tracking

Within each section, order by composite score descending.

## Step 4 — Write the digest

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
---

# AI Tool Digest — {D Month YYYY}

_Coverage: {since date formatted as D Month YYYY} to {fetched_at date formatted as D Month YYYY}_

## {Section heading}

### {Item title}
**Source**: {source} | **Date**: {D Mon YYYY} | **Signal**: {composite score to 1 decimal place}

{2-4 sentences. State what this is, why it matters to a senior software engineer or architect, and what concrete action or change in practice it suggests.}

[Source]({url})

---
{blank line between items}

## Excluded items

| Title | Source | Reason |
|---|---|---|
| {truncated title, max 60 chars} | {source} | {one-line reason} |
```

After writing, report the output path and the count of items included.
