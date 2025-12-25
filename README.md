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


## ⚡ Performance

Evicta is designed to keep the **hot path extremely fast** while still enabling **controlled semantic reuse** during cache misses.  
The system prioritizes microsecond-level access for cache hits, ensuring it can safely sit in front of high-throughput LLM workloads.

> **Note:** All benchmarks were measured on a local development machine and represent *relative performance*, not absolute production guarantees. Results will vary by hardware, OS, and Python runtime.


## 🧪 Benchmark Scenarios

| Operation            | Description                                              |
|---------------------|----------------------------------------------------------|
| Exact cache hit     | Prompt matches an existing cached entry                  |
| Intent cache hit    | Prompt matches an entry via semantic intent reuse        |
| Cache miss          | Prompt not found and falls back to lookup + processing   |


## 📊 Representative Results (Rule-Based Intent Engine)

--- Evicta Benchmarks ---
| Operation            | Description   |
|---------------------|----------------|
| Exact cache hit          |   ~2.7 µs |
| Intent cache hit          |  ~2.5 µs |
| Cache miss (Rule based intent) | ~5.2 µs |

## ML-Based Intent Classifier (Optional)

Evicta can optionally use a lightweight machine-learned intent classifier to improve semantic reuse across structurally different but semantically equivalent prompts.

When enabled, cache misses incur additional latency due to local model inference:

Operation: Latency
Cache miss (ML intent model): ~3–4 ms

1. Cache hits remain microsecond-level
2. Cache misses incur a small millisecond-level penalty
3. Still orders of magnitude faster than full LLM inference (which often takes hundreds of milliseconds to seconds)

##  Interpretation

Cache hits completely avoid model execution and return in microseconds.
Rule-based intent reuse adds negligible overhead.
ML-based intent classification trades a small miss-time penalty for higher semantic reuse accuracy.
Both modes remain vastly cheaper than repeated LLM calls.
