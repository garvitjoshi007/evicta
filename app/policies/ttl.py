"""
Time-to-live (TTL) policy for cache entries.

This module determines the expiration time for cached responses. Currently implements
a simple fixed TTL policy, but can be extended to support intent-based or
prompt-pattern-based TTL strategies.

Example:
    >>> get_ttl("what is AI?")
    86400  # 1 day
"""


def get_ttl() -> int:
    """
    Determine the time-to-live (TTL) for a cache entry in seconds.

    Currently returns a fixed TTL of 1 day (86400 seconds) for all prompts.
    This function is a placeholder for future policy logic (e.g. intent-based TTL).

    Args:
        prompt: The user prompt (may be used in future implementations).

    Returns:
        TTL in seconds (int).
    """
    return 86400
