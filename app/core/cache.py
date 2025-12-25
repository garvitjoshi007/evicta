"""
Cache interface and operations.

This module provides the high-level caching API with prompt cleaning, cache
retrieval, and storage. It integrates with the low-level cache_store module
for data management and the intent extraction module for semantic matching.

Key features:
    - Prompt normalization (case, whitespace, Unicode handling)
    - TTL-based expiration
    - LRU eviction policy
    - Intent-based cache lookups
    - Prompt and intent-to-entry associations
"""

import time
import unicodedata

from app.core import cache_store
from app.semantic import intent


def clean(prompt: str) -> str:
    """
    Normalize a user prompt for consistent cache lookups.

    Removes Unicode format characters (e.g. zero-width spaces) and normalizes
    the prompt to lowercase with uniform whitespace (single spaces between words).

    Args:
        prompt: The raw user prompt string.

    Returns:
        A normalized prompt string.

    Example:
        >>> clean("  Hello   WORLD  ")
        "hello world"
    """
    # Remove Unicode "format" characters (e.g. zero-width space)
    prompt = "".join(ch for ch in prompt if unicodedata.category(ch) != "Cf")

    # Normalize case and whitespace
    return " ".join(prompt.lower().split())


def get_from_cache(prompt: str) -> str | None:
    """
    Retrieve a cached response by prompt or intent.

    First normalizes the prompt and attempts a direct lookup. If that fails,
    extracts the intent and tries an intent-based lookup. Associates the prompt
    to the entry if found via intent matching.

    Args:
        prompt: The user prompt to look up.

    Returns:
        The cached response string if found, otherwise None.
    """
    prompt = clean(prompt)

    # 1. Exact match
    hit = cache_store.get_entry_by_prompt(prompt)
    if hit is not None:
        return hit

    # 2. Intent reuse
    intent_key = intent.extract_intent(prompt)
    if intent_key and should_try_intent(prompt):
        entry_id = cache_store.intent_to_entry_id.get(intent_key)
        if entry_id is not None:
            entry = cache_store.cache_entries.get(entry_id)
            if entry and time.time() <= entry["expires_at"]:
                cache_store.mru_update(entry_id)
                cache_store.associate_prompt_to_entry(prompt, entry_id)
                return entry["response"]

    return None


def set_in_cache(prompt: str, response: str, ttl_seconds: int) -> None:
    """
    Store a response in the cache with an associated prompt and TTL.

    Normalizes the prompt, creates or updates a cache entry, associates the
    prompt and any extracted intent to the entry, and enforces LRU eviction
    if the cache exceeds MAX_CACHE_SIZE.

    Args:
        prompt: The normalized user prompt.
        response: The response text to cache.
        ttl_seconds: Time-to-live in seconds for this cache entry.

    Returns:
        None
    """
    prompt = clean(prompt)

    # check if the prompt already points to an entry
    entry_id = cache_store.get_entry_id_by_prompt(prompt)
    if entry_id is not None:
        cache_store.cache_entries[entry_id]["response"] = response
        cache_store.cache_entries[entry_id]["expires_at"] = time.time() + ttl_seconds
        cache_store.mru_update(entry_id)
        return

    # create new entry
    entry_id = cache_store.create_entry(response, ttl_seconds)
    cache_store.associate_prompt_to_entry(prompt, entry_id)

    # register intent if it exists
    intent_key = intent.extract_intent(prompt)
    if intent_key and should_try_intent(prompt):
        cache_store.associate_intent_to_entry(intent_key, entry_id)

    # enforce capacity limitations
    if len(cache_store.cache_entries) > cache_store.MAX_CACHE_SIZE:
        oldest_entry_id = next(iter(cache_store.cache_entries))
        cache_store.evict_entry(oldest_entry_id)


def show_cache():
    """
    Return the entire cache contents.

    Returns:
        The OrderedDict of cache entries (key: entry_id, value: entry data).
    """
    return cache_store.cache_entries


def json_safe(obj):
    """
    Recursively convert an object to JSON-safe types.

    Converts dicts, lists, tuples, and sets, preserving ints, floats, strings,
    bools, and None. Non-JSON-safe objects are converted to their repr() string.

    Args:
        obj: Any Python object.

    Returns:
        A JSON-serializable representation of obj.
    """
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [json_safe(x) for x in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    return repr(obj)  # force any internal engine object to string


def show_prompts_mapping():
    """
    Return the prompt-to-entry and entry-to-prompts mappings.

    Returns:
        A dict with keys 'prompt_to_entry_id' and 'entry_id_to_prompts',
        both JSON-safe.
    """
    return {
        "prompt_to_entry_id": json_safe(cache_store.prompt_to_entry_id),
        "entry_id_to_prompts": json_safe(cache_store.entry_id_to_prompts),
    }


def show_intents_mapping():
    """
    Return the intent-to-entry and entry-to-intents mappings.

    Returns:
        A dict with keys 'intent_to_entry_id' and 'entry_id_to_intents',
        both JSON-safe.
    """
    return {
        "intent_to_entry_id": json_safe(cache_store.intent_to_entry_id),
        "entry_id_to_intents": json_safe(cache_store.entry_id_to_intents),
    }

def should_try_intent(prompt: str) -> bool:
    """
    Return if the prompt to intent conversion is worth the effort (few perf guardrails)

    Returns: 
        A boolean True or False
    """
    if len(prompt) > 80:
        return False
    if any(c.isdigit() for c in prompt):
        return False
    if "\n" in prompt:
        return False
    return True
