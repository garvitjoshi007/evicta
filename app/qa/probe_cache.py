import time
from app.core.cache import set_in_cache, get_from_cache, show_cache, CACHE

def reset_cache():
    CACHE.clear()
    print("\n--- CACHE RESET ---\n")


# -------------------------
# NORMALIZATION TESTS
# -------------------------

def test_expected_equivalence():
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
    print("TEST 2: Expected distinction (should MISS)")
    reset_cache()

    set_in_cache("hello", "response-plain", 10)
    res = get_from_cache("hello?")
    
    print("get_from_cache('hello?') ->", res)
    print("Cache contents:", show_cache())
    print("Expected cache size = 1 (MISS, no reuse)\n")


def test_whitespace_variants():
    print("TEST 3: Whitespace edge cases")
    reset_cache()

    set_in_cache("What is AI", "ai-definition", 10)

    variants = [
        "What  is   AI",
        "What is AI\n",
        "What is\tAI",
        "What is AI\u00a0",   # non-breaking space
        "What is AI\u200b",   # zero-width space
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
    for k in CACHE.keys():
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
