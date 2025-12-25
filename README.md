# Evicta

Evicta is a correctness-first cache engine for AI inference workloads.
It enables safe reuse of LLM responses while enforcing freshness, eviction, and lifecycle guarantees.

Evicta is designed to be embedded inside applications (API servers, agents, workers) to reduce redundant model calls without risking incorrect cache hits.

This project focuses on building strong cache invariants first, and progressively layering controlled semantic reuse, dynamic TTL reasoning, and AI-assisted staleness inspection.

## Why Evicta

Blind caching of AI responses is dangerous — incorrect reuse leads to silent data corruption and loss of trust.

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
