# Design: Digest Trend Tracking

Date: 2026-05-31
Status: Accepted
Revised: 2026-05-31 (post design-review)

## Problem

Each digest run produces a standalone markdown file capturing AI tool signals from a fixed time window. There is no mechanism to detect whether a topic is new, rising, steady, or fading relative to prior runs. Two additions are needed:

1. **Overview** — an executive summary of what the current digest contains, written at synthesis time
2. **Trend Summary** — a data-driven section showing which topics are rising, steady, new, or cooling compared to recent history

Both sections appear at the top of each digest file, before the per-item sections.

## Constraints

- The skill runs inside Claude Code; no always-on process, no external services
- The Python script handles fetching only; synthesis, trend computation, and writing happen inside the Claude skill
- No new Python dependencies for the initial implementation
- JSON storage must be outside `news/` to avoid clutter — `data/` subdirectory
- The schema must be forward-compatible with a future embedding-based topic clustering upgrade without requiring a migration

## Options considered

**Option 1 — Tag ledger with LLM-assigned tags**: Claude extracts normalised topic tags per item during synthesis, appends a structured run record to a single cumulative JSON file, reads that file at the start of each run to compute trend trajectories. No new dependencies. Tag consistency maintained by passing the existing vocabulary as context to Claude at tag-assignment time.

**Option 2 — Embedding-based topic tracking**: Python script embeds each item's title+snippet using `sentence-transformers`, clusters across runs, stores cluster IDs. More robust semantic grouping but adds a ~500 MB model dependency and slows the fetch step substantially. Marginal quality gain over Option 1 may not justify the cost at this stage.

**Option 3 — Tag ledger now, embeddings as optional upgrade path** *(chosen)*: Implements Option 1 with a schema that includes a `cluster_id` field set to `null`, ready to be populated by a future optional embedding pass. Ships immediately with no new dependencies; keeps the upgrade path open without committing to it.

## Decision

Implement Option 3.

### Ledger schema

Single file at `data/signal-ledger.json`. Structure:

```json
{
  "version": 1,
  "runs": [
    {
      "date": "2026-05-31T11:12:00+00:00",
      "digest_file": "news/2026-05-31-1112.md",
      "item_count": 14,
      "topics": [
        {
          "tag": "Claude Code",
          "count": 3,
          "avg_signal": 7.3,
          "cluster_id": null
        }
      ]
    }
  ]
}
```

`tag` values are normalised short labels (e.g. "Claude Code", "MCP", "agent memory", "RAG", "local inference"). Claude assigns these during synthesis using the existing tag vocabulary from the ledger as reference context, to maintain consistency across runs.

### Trend computation

Lookback windows:
- **Recent**: last 7 runs
- **Baseline**: last 30 runs

For each tag, compute appearance rate (runs in which tag appeared / total runs) for each window. Classify:

| Classification | Condition |
|---|---|
| New | Fewer than 3 lifetime appearances |
| Rising | Recent rate > baseline rate by meaningful margin |
| Steady | Recent and baseline rates roughly equal |
| Cooling | Recent rate < baseline rate by meaningful margin |
| Resurfaced | Zero appearances in last 14 runs, now reappears |

"Meaningful margin" provisional thresholds (subject to revision once cadence stabilises):
- **Rising**: recent rate > baseline rate by >= 0.20
- **Steady**: rates within 0.15 of each other
- **Cooling**: recent rate < baseline rate by >= 0.20
- **Resurfaced**: absent from the most recent 7 runs, now reappears

On first use (fewer than 3 prior runs), skip the trend summary entirely. With 3–6 prior runs, include the summary labelled "_Provisional — based on fewer than 7 prior runs._"

### Digest structure change

```
---
(front matter — add top_tags field: list of up to 5 tag strings,
 ordered by item count descending within this digest, e.g.:
 top_tags:
   - Claude Code
   - MCP
   - agent memory)
---

# AI Tool Digest — {date}

_Coverage: ..._

## Overview

{3–5 sentences. What domains dominate this digest? Any standout high-signal items? What is absent that appeared recently?}

## Trend Summary

**Rising**: {tag, tag, tag}
**New this period**: {tag, tag}
**Steady**: {tag, tag, tag}
**Cooling**: {tag, tag}

_Based on {N} prior runs. Trend window: recent = last 7 runs, baseline = last 30 runs._

## {Sections as before...}
```

### Skill changes

The digest skill gains three new steps inserted around the existing flow:

**Before Step 2 (before scoring)**: Read `data/signal-ledger.json` if it exists. Handle failure modes gracefully:
- File missing: treat as empty ledger, no warning
- File exists but not valid JSON: emit a warning and continue without trend history; do not abort
- File exists, valid JSON, but `version != 1`: emit a warning and continue without trend history; do not abort

Extract the existing tag vocabulary (top 50 tags by lifetime frequency). Hold this for use during tag assignment. If fewer than 3 prior runs exist, note that trend summary will be skipped. If 3–6 prior runs exist, the trend summary will be labelled provisional.

**After Step 3 (after synthesis, before writing)**: For each retained item, assign 1–3 normalised topic tags drawn from the existing vocabulary where possible. New tags are permitted when no existing tag is an adequate match, but should be kept to a minimum. Compute trend classifications. Write the Overview paragraph.

**After Step 4 (after writing the digest)**: Reconstruct the complete ledger document (all prior runs plus the new run record) and write it in full to `data/signal-ledger.json` using the Write tool. Writing the complete document — never a partial append — ensures that a write failure leaves either the previous complete file or the new complete file, never a hybrid. Create the `data/` directory if it does not exist.

## Consequences

**Easier**:
- Each digest immediately gains interpretive context about whether its signals represent fresh developments or sustained trends
- The ledger accumulates a structured history that can power richer analysis later
- The `cluster_id` field keeps the embedding upgrade path open at zero cost now

**Harder**:
- Tag vocabulary drift is possible if Claude introduces near-synonyms across runs (e.g. "MCP servers" vs "MCP"); mitigated by passing the top-50 tags as context but not fully eliminated
- The top-50 vocabulary cap prevents unbounded context growth; tags outside the top 50 are still stored in the ledger for trend computation but not passed as context
- The skill prompt grows longer with the additional steps; worth monitoring for context budget impact on long-running digests

**Risks**:
- Trend window (7/30 runs) is a guess; if digests are run more than once per day, "7 runs" may span only a week, which is probably too short for meaningful trend detection. Revisit once cadence stabilises.
- First 30 runs will produce incomplete baselines; the trend summary should be clearly labelled as provisional during this warmup period
