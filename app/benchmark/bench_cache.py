"""
Cache performance benchmarking suite.

This module provides benchmarking utilities to measure the performance of cache
operations (exact hits, intent-based hits, and misses). It uses time.perf_counter()
for high-resolution timing and reports average execution time in microseconds.

Test Scenarios:
    - Exact cache hit: Prompt exactly matches a cached entry.
    - Intent cache hit: Prompt matches via intent extraction (semantic match).
    - Cache miss: Prompt not found in cache.

Usage:
    python -m app.benchmark.bench_cache

Example:
    >>> bench("Sample operation", lambda: 1 + 1, runs=1000)
    Sample operation         : 0.10 µs
"""

import time
from app.core.cache import set_in_cache, get_from_cache
from app.services.llm import generate_response

PROMPT_EXACT = "what is ai"
PROMPT_INTENT = "define ai"
PROMPT_MISS = "who invented pizza"

def llm(prompt):
    """
    Generate an LLM response for a given prompt.

    Wraps the generate_response service to provide a simple interface
    for benchmarking LLM calls.

    Args:
        prompt: The input prompt to send to the LLM.

    Returns:
        The generated response text from the LLM service.
    """
    return generate_response(prompt)

def bench(name, fn, runs=10_000):
    """
    Benchmark a function by measuring execution time over multiple runs.

    Executes the provided function 'runs' times and reports the average
    execution time in microseconds.

    Args:
        name: A descriptive name for the benchmark (left-aligned in output).
        fn: A callable (function or lambda) to benchmark.
        runs: Number of times to execute fn (default: 10,000).

    Returns:
        None (prints results to stdout).

    Example:
        >>> bench("Test", lambda: 1 + 1, runs=1000)
        Test                     : 0.05 µs
    """
    start = time.perf_counter()
    for _ in range(runs):
        fn()
    end = time.perf_counter()
    avg = (end - start) / runs * 1e6
    print(f"{name:<25}: {avg:.2f} µs")

# Prime cache
set_in_cache(PROMPT_EXACT, llm(PROMPT_EXACT), 3600)

# Intent-based entry
set_in_cache(PROMPT_INTENT, llm(PROMPT_INTENT), 3600)

print("\n--- Evicta Benchmarks ---")

bench("Exact cache hit", lambda: get_from_cache(PROMPT_EXACT))
bench("Intent cache hit", lambda: get_from_cache(PROMPT_INTENT))
bench("Cache miss", lambda: get_from_cache(PROMPT_MISS))
# bench("Fake LLM call", lambda: llm(PROMPT_MISS))
