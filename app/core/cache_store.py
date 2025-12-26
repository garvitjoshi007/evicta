"""
Low-level cache storage and entry management.

This module provides the authoritative data structures and operations for managing
cache entries, associations between prompts/intents and entries, and LRU ordering.
It handles:
    - Entry creation and eviction
    - Prompt-to-entry associations
    - Intent-to-entry associations
    - MRU (most-recently-used) tracking via OrderedDict
    - TTL management and expiration checks

Global State:
    cache_entries: OrderedDict mapping entry_id to entry data (response + expires_at).
    prompt_to_entry_id: Dict mapping normalized prompts to entry IDs.
    entry_id_to_prompts: Dict mapping entry IDs to sets of associated prompts.
    intent_to_entry_id: Dict mapping intent keys to entry IDs.
    entry_id_to_intents: Dict mapping entry IDs to sets of associated intents.
"""

import time
import uuid
from collections import OrderedDict

cache_entries = OrderedDict()  # authoritative -> Key: entry_id , Value: entry data
prompt_to_entry_id = {}  # just for lookup -> Key: normalized prompt , Value: entry_id
entry_id_to_prompts = {}  # for cleanups -> Key: entry_id , Value: set of prompts
intent_to_entry_id = {}  # for intent mapping: Key: intent_key, Value: entry_id
entry_id_to_intents = {}  # for cleanups -> Key: entry_id, Value: set of intents

MAX_CACHE_SIZE = 10


def mru_update(entry_id: str) -> None:
    """
    Update the most-recently-used position of a cache entry.

    Moves the entry to the end of the OrderedDict to track LRU order.

    Args:
        entry_id: The ID of the cache entry to mark as recently used.

    Returns:
        None
    """
    cache_entries.move_to_end(entry_id)


def create_entry(response: str, ttl_seconds: int) -> str:
    """
    Create a new cache entry and return its ID.

    Initializes the entry with response text and expiration time, creates
    associated prompt and intent sets, and increments the global entry ID counter.

    Args:
        response: The response text to store.
        ttl_seconds: Time-to-live in seconds.

    Returns:
        The newly created entry_id (int).
    """
    entry_id = uuid.uuid4().hex[:8]
    cache_entries[entry_id] = {
        "response": response,
        "expires_at": time.time() + ttl_seconds,
    }
    entry_id_to_prompts[entry_id] = set()
    entry_id_to_intents[entry_id] = set()
    return entry_id


def associate_prompt_to_entry(prompt: str, entry_id: str) -> None:
    """
    Associate a prompt to a cache entry.

    If the prompt was previously associated with a different entry, removes it
    from that entry's set first. Then adds the new association.

    Args:
        prompt: The normalized prompt string.
        entry_id: The ID of the cache entry.

    Returns:
        None
    """
    # Remove prompt from old entry if it exists
    old_entry_id = prompt_to_entry_id.get(prompt)
    if old_entry_id:
        entry_id_to_prompts[old_entry_id].discard(prompt)

    # Add new mapping
    prompt_to_entry_id[prompt] = entry_id
    entry_id_to_prompts[entry_id].add(prompt)


def associate_intent_to_entry(intent: str, entry_id: str) -> None:
    """
    Associate an intent to a cache entry.

    If the intent was previously associated with a different entry, removes it
    from that entry's set first. Then adds the new association.

    Args:
        intent: The intent key (e.g. "DEFINE:topic").
        entry_id: The ID of the cache entry.

    Returns:
        None
    """
    # Remove prompt from old entry if it exists
    old_entry_id = intent_to_entry_id.get(intent)
    if old_entry_id:
        entry_id_to_intents[old_entry_id].discard(intent)

    # Add new mapping
    intent_to_entry_id[intent] = entry_id
    entry_id_to_intents[entry_id].add(intent)


def get_entry_id_by_prompt(prompt: str) -> str | None:
    """
    Get the entry ID associated with a prompt.

    Args:
        prompt: The normalized prompt string.

    Returns:
        The entry_id if found, otherwise None.
    """
    return prompt_to_entry_id.get(prompt)


def get_entry_by_prompt(prompt: str) -> str | None:
    """
    Retrieve a cached response by prompt with TTL and LRU checks.

    Looks up the entry by prompt, checks if it has expired, marks it as
    most-recently-used if valid, and evicts it if expired.

    Args:
        prompt: The normalized prompt string.

    Returns:
        The cached response string if found and not expired, otherwise None.
    """
    entry_id = prompt_to_entry_id.get(prompt)

    if entry_id is None:
        return None

    entry = cache_entries.get(entry_id)
    if entry is None:
        return None

    # check ttl
    if time.time() > entry["expires_at"]:
        evict_entry(entry_id)
        return None

    # update mru
    mru_update(entry_id)

    return entry.get("response")


def evict_entry(entry_id: str):
    """
    Remove a cache entry and all its associated prompt and intent mappings.

    Cleans up the entry from cache_entries and all related lookup dictionaries.

    Args:
        entry_id: The ID of the cache entry to evict.

    Returns:
        None
    """
    cache_entries.pop(entry_id, None)

    # for getting all prompts pointing to this entry
    prompts = entry_id_to_prompts.pop(entry_id, set())

    # remove prompt -> entry mapping
    for prompt in prompts:
        prompt_to_entry_id.pop(prompt)

    intents = entry_id_to_intents.pop(entry_id, set())

    for intent in intents:
        intent_to_entry_id.pop(intent)
