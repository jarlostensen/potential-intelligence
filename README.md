# Claude Intelligence

An autonomous research and synthesis system for tracking advanced LLM usage patterns, tooling, and workflows as they emerge among expert practitioners.

## What it does

Runs a `/digest` skill inside Claude Code that fetches signals from curated free public sources, scores each item against a signal ranking framework, synthesises findings into a structured markdown digest, and accumulates a cross-run trend ledger so subsequent digests can classify topics as rising, new, steady, cooling, or resurfaced.

The output is a growing `news/` directory of dated digests covering:

- Claude, Anthropic releases, MCP ecosystem
- LLM model developments and benchmarks
- Agent engineering: orchestration, memory, tool use
- AI-assisted software development workflows
- Cloud and infrastructure for AI deployment
- Native/C++ client-side AI and local inference
- Tools and frameworks worth tracking

## Structure

```
.claude/skills/digest/   # /digest skill definition
scripts/                 # Python fetch script (uv)
news/                    # Generated digests (YYYY-MM-DD-HHMM.md)
data/                    # signal-ledger.json — cross-run trend data
docs/
  adr/                   # Architecture decision records
  design/                # Design notes
```

## Running a digest

```
/digest
```

Or with an explicit since-date to override the auto-detected window:

```
/digest --since 2026-05-30
```

Requires [uv](https://docs.astral.sh/uv/) to be installed. The fetch script pulls from Hacker News, Reddit (RSS), curated RSS feeds, and GitHub Search — all free and unauthenticated.

### RSS sources

- Simon Willison
- Latent Space
- LessWrong
- The Gradient
- Interconnects
- Pragmatic Engineer
- Chip Huyen
- LangChain Blog
- r/LocalLLaMA
- r/ClaudeAI

## Signal ranking

Each fetched item is scored on five dimensions:

| Dimension | Weight |
|---|---|
| Impact | 0.35 |
| Novelty | 0.20 |
| Adoption Velocity | 0.20 |
| Repeatability | 0.15 |
| Generality | 0.10 |

Items scoring below 4.0 are discarded. Items that are primarily product announcements, lack reproducible evidence, or are off-topic are discarded regardless of score. The scoring is done by Claude at synthesis time; the Python script only handles fetching.

## Trend tracking

After the third run, each digest includes:

- **Overview** — 3–5 sentence executive summary of what domains dominate and what's absent
- **Trend Summary** — topic classifications derived from the cross-run ledger (`data/signal-ledger.json`)

Topic classifications:

| Label | Condition |
|---|---|
| New | Fewer than 3 lifetime appearances in the ledger |
| Rising | Recent appearance rate > baseline by 0.20+ |
| Steady | Recent and baseline rates within 0.15 |
| Cooling | Recent rate < baseline by 0.20+ |
| Resurfaced | Absent from last 7 runs, now reappears |

Windows: recent = last 7 runs, baseline = last 30 runs. The ledger schema includes a `cluster_id: null` field reserved for a future embedding-based topic clustering upgrade.

## Design decisions

- [ADR-0001](docs/adr/0001-use-tag-ledger-for-digest-trend-tracking.md) — tag ledger with forward-compatible schema for trend tracking
- [Design note](docs/design/digest-trend-tracking.md) — detailed rationale, options considered, consequences

## Cadence

Run once daily for best results. The auto-detected `since` date is read from the most recent digest's front matter. Running more than once per day produces a very narrow window with few new items.
