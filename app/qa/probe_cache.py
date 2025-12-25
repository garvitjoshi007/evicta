"""
Cache probing and test suite.

This module provides a comprehensive set of test functions to validate cache behavior
including normalization, TTL expiration, LRU eviction, and intent-based matching.
These tests verify the correctness of the caching system under various edge cases.

Test Categories:
    - Normalization: Case/whitespace handling
    - Distinction: Different prompts are cached separately
    - Whitespace: Various Unicode and special whitespace characters
    - TTL: Time-to-live expiration behavior
    - LRU: Least-recently-used eviction under capacity constraints

Usage:
    python -m app.qa.probe_cache

Example:
    >>> test_expected_equivalence()
    TEST 1: Expected equivalence (should HIT)
    --- CACHE RESET ---
    ...
"""

import time

from app.core.cache import get_from_cache, set_in_cache, show_cache
from app.core import cache_store


def reset_cache():
    """
    Clear all cache entries and print a reset message.

    Used by test functions to ensure a clean slate before each test.

    Returns:
        None
    """
    cache_store.cache_entries.clear()
    print("\n--- CACHE RESET ---\n")


# -------------------------
# NORMALIZATION TESTS
# -------------------------


def test_expected_equivalence():
    """
    Test that prompt normalization treats case/whitespace variants as equivalent.

    Sets a cache entry with "Hello" and verifies that various case and whitespace
    variants retrieve the same cached response.

    Returns:
        None
    """
    print("TEST 1: Expected equivalence (should HIT)")
    reset_cache()

    set_in_cache("Hello", "response-hello", 10)

    variants = [
        "hello",
        " HELLO ",
        "HeLLo",
        "hello   ",
    ]

    for v in variants:
        res = get_from_cache(v)
        print(f"get_from_cache({repr(v)}) -> {res}")

    print("Cache contents:", show_cache())
    print("Expected cache size = 1\n")


def test_expected_distinction():
    """
    Test that different prompts are cached separately.

    Sets a cache entry for "hello" and verifies that "hello?" is not found
    (even though it's similar), resulting in a cache miss.

    Returns:
        None
    """
    print("TEST 2: Expected distinction (should MISS)")
    reset_cache()

    set_in_cache("hello", "response-plain", 10)
    res = get_from_cache("hello?")

    print("get_from_cache('hello?') ->", res)
    print("Cache contents:", show_cache())
    print("Expected cache size = 1 (MISS, no reuse)\n")


def test_whitespace_variants():
    """
    Test handling of various whitespace characters in normalization.

    Sets a cache entry for "What is AI" and tests retrieval with different
    whitespace characters (spaces, tabs, newlines, non-breaking spaces,
    zero-width spaces) to verify normalization behavior.

    Returns:
        None
    """
    print("TEST 3: Whitespace edge cases")
    reset_cache()

    set_in_cache("What is AI", "ai-definition", 10)

    variants = [
        "What  is   AI",
        "What is AI\n",
        "What is\tAI",
        "What is AI\u00a0",  # non-breaking space
        "What is AI\u200b",  # zero-width space
    ]

    for v in variants:
        res = get_from_cache(v)
        print(f"get_from_cache({repr(v)}) -> {res}")

    print("Cache contents:", show_cache())
    print("Observe which variants HIT vs MISS\n")


# -------------------------
# TTL + NORMALIZATION INTERACTION
# -------------------------


def test_ttl_boundary():
    """
    Test that cache entries expire after their TTL.

    Sets a cache entry with a 1-second TTL, waits for expiration, and verifies
    that retrieval returns None and the cache is empty.

    Returns:
        None
    """
    print("TEST 4: TTL boundary behavior")
    reset_cache()

    set_in_cache("temp key", "short-lived", 1)
    time.sleep(1.1)

    res = get_from_cache(" temp   key ")
    print("get_from_cache after TTL ->", res)
    print("Cache contents:", show_cache())
    print("Expected: MISS and cache empty\n")


# -------------------------
# LRU + NORMALIZATION INTERACTION
# -------------------------


def test_lru_with_similar_keys():
    """
    Test LRU eviction when cache capacity is exceeded.

    Sets cache entries for "a", "b", "c", accesses "a" to mark it as most-recently-used,
    then adds "d" to force eviction. Verifies that the least-recently-used entry ("b")
    is evicted.

    Returns:
        None
    """
    print("TEST 5: LRU with similar-looking keys")
    reset_cache()

    set_in_cache("a", "A", 10)
    set_in_cache("b", "B", 10)
    set_in_cache("c", "C", 10)

    # Access "a" so it becomes MRU
    get_from_cache("A")

    # Add new entry to force eviction
    set_in_cache("d", "D", 10)

    print("Cache contents (order matters):")
    for k in cache_store.cache_entries.keys():
        print(k)

    print("\nExpected eviction: 'b' (if MAX_CACHE_SIZE = 3)\n")


# -------------------------
# RUN ALL PROBES
# -------------------------

if __name__ == "__main__":
    test_expected_equivalence()
    test_expected_distinction()
    test_whitespace_variants()
    test_ttl_boundary()
    test_lru_with_similar_keys()
