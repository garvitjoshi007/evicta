# Evicta

Evicta is a cache engine built specifically for AI inference workloads.
Its goal is to reuse model responses safely while preserving freshness, eviction order, and correctness guarantees.

Evicta is meant to be embedded directly inside applications such as API servers, background workers, and agent systems to reduce redundant model calls without risking incorrect cache hits.

The project starts with strict cache invariants and a deterministic core, and then gradually adds controlled semantic reuse, dynamic TTL strategies, and experimental AI-assisted staleness reasoning.

## Why Evicta

Blind caching of AI responses is dangerous, incorrect reuse leads to silent data corruption and loss of trust.

Evicta is built around three core principles:

* Identity over lookup: cached responses have stable identities independent of prompts
* Correct eviction semantics: no dangling or stale references are ever served
* Safe reuse before smart reuse:deterministic correctness first, semantic reuse later

## Core Features

1. Entry-ID based cache architecture
2. Prompt normalization & Unicode-safe matching
3. TTL-based freshness control
4. LRU eviction with full referential cleanup
5. Multi-prompt → single-entry mapping
6. Deterministic cache invariants

## Roadmap

| Phase | Feature                                   | Status |
|------:|-------------------------------------------|:------:|
| 1     | Exact match caching with TTL + LRU         | ✅     |
| 2     | Entry-ID architecture & referential cleanup| ✅     |
| 3     | Deterministic intent-based reuse           | ⏳     |
| 4     | Embedding-based semantic reuse             | ⏳     |
| 5     | AI-assisted TTL inspection & soft staleness| ⏳     |
| 6     | Metrics, observability & QA probes         | ⏳     |
