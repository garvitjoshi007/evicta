# Evicta

Evicta is an experimental cache system for AI inference workloads, designed to reuse LLM responses while managing freshness and eviction intelligently.

The project is aimed to perform simple deterministic caching and progressively adds semantic similarity, soft TTLs, and AI-assisted staleness reasoning.

This is a learning and research-oriented project, not a production library.

## Goals
- Reduce redundant AI inference
- Model cache staleness beyond fixed TTLs
- Explore AI-assisted cache management safely

## Non-goals
- Replacing Redis or existing cache systems
- Fully autonomous decision-making
- Solving general knowledge correctness

## Status
Early development.


## To DO 
1. Semantic caching (embedding-based reuse)
2. Agentic TTL inspector (dynamic TTL assignment)
3. Attack-resilience (prompt obfuscation & abuse cases)
4. Metrics & observability (hit ratio, eviction rate)