---
status: accepted
date: 2026-05-31
deciders: Jarl Ostensen
consulted: Claude (design session)
informed: —
---

# Use Tag Ledger with Forward-Compatible Schema for Digest Trend Tracking

## Context and Problem Statement

The digest skill generates standalone markdown files per run. There is no mechanism to detect whether a topic is new, rising, steady, or fading relative to prior runs. Each digest is therefore read without interpretive context about the broader trajectory of its signals. Adding a cross-run trend summary and an executive overview requires a persistent, structured record of what each run covered, suitable for querying at synthesis time.

## Decision Drivers

* The skill must run inside Claude Code with no always-on process or external services
* No new Python dependencies should be required for the initial implementation
* The storage schema must be forward-compatible with a future embedding-based topic clustering upgrade without requiring a migration
* KISS: the simplest solution that satisfies the requirements is preferred
* The `data/` subdirectory is used to keep structured artefacts out of `news/`

## Considered Options

* Option 1 — LLM-assigned tag ledger (minimal schema)
* Option 2 — Embedding-based semantic clustering
* Option 3 — Tag ledger now, forward-compatible schema for embeddings later

## Decision Outcome

Chosen option: "Option 3 — Tag ledger now, forward-compatible schema for embeddings later", because it ships cross-run trend detection immediately with no new dependencies, and the `cluster_id: null` field in the ledger schema preserves the embedding upgrade path at zero present cost.

### Positive Consequences

* Each digest immediately gains a Trend Summary and Overview section, providing interpretive context without manual work
* The cumulative ledger at `data/signal-ledger.json` accumulates structured history that can power richer analysis in future
* No new Python dependencies; all trend computation happens inside the Claude synthesis steps
* The `cluster_id` field makes a future embedding pass a drop-in enhancement, not a migration

### Negative Consequences

* Tag vocabulary consistency depends on Claude passing the existing vocabulary as context at tag-assignment time; near-synonym drift (e.g. "MCP servers" vs "MCP") is mitigated but not fully eliminated
* The skill prompt grows longer with three new steps; context budget should be monitored on long-running digests
* Trend windows (7 runs recent / 30 runs baseline) are initial guesses; first 30 runs will produce provisional baselines

## Pros and Cons of the Options

### Option 1 — LLM-assigned tag ledger (minimal schema)

Claude assigns normalised topic tags per retained item, appends a run record to a single cumulative JSON file, reads that file at the start of each run to compute appearance-rate trajectories.

* Good, because no new dependencies required
* Good, because tag assignment leverages Claude's existing semantic understanding
* Good, because the simplest possible implementation of cross-run tracking
* Bad, because the schema has no upgrade path to embedding-based clustering; adding `cluster_id` later would require a migration over all existing run records

### Option 2 — Embedding-based semantic clustering

The Python script embeds each item's title and snippet using `sentence-transformers`, clusters embeddings across runs to form stable topic identities, stores cluster IDs in the ledger.

* Good, because semantic grouping is more robust than string-matched tags (handles paraphrases and near-synonyms automatically)
* Bad, because adds approximately 500 MB of model dependency to the fetch script
* Bad, because slows the fetch step substantially and requires a network round-trip or local model load on every run
* Bad, because the marginal quality gain over Option 1 does not justify the complexity at this stage

### Option 3 — Tag ledger now, forward-compatible schema for embeddings later

Implements Option 1 with a `cluster_id: null` field added to each topic record from day one, ready to be populated by an optional future embedding pass.

* Good, because ships immediately with no new dependencies (identical runtime cost to Option 1)
* Good, because the `cluster_id` field makes a semantic clustering upgrade a non-breaking additive change
* Good, because the tag vocabulary passed as context to Claude grows richer over time, reducing synonym drift organically
* Bad, because tag consistency still depends on Claude's discipline; the `cluster_id` field only pays off if the embedding upgrade is eventually implemented

## More Information

* Design note: [docs/design/digest-trend-tracking.md](../design/digest-trend-tracking.md)
* Ledger location: `data/signal-ledger.json` (created on first digest run after implementation)
* Ledger schema version: `1`; increment if breaking changes are made to the run record structure
* Trend windows — 7 runs (recent), 30 runs (baseline) — should be revisited once digest cadence stabilises
* The git-dirty question (whether to commit the ledger after each run) is not decided by this ADR and should be addressed when the ledger is first committed
