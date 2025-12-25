"""
Intent extraction utilities.

This module provides helpers to extract a normalized intent identifier
from a user prompt. The extraction attempts to match the prompt against
a set of simple intent regex patterns and returns a compact intent key
of the form "<INTENT>:<subject>" on success or None on failure.

Workflow (high level):
1. Normalize prompt (outside this module)
2. Try prompt_to_entry lookup (outside this module)
3. If miss → extract_intent(prompt)
4. If intent exists → try intent_to_entry lookup (outside this module)
5. If found → return entry (and bind this prompt to it) (outside)

Example:
    >>> extract_intent("What is AI?")
    "DEFINE:ai"
"""

import re

INTENT_PATTERNS = [
    ("DEFINE", r"(?:what is|what\'s)\s+(?P<subject>.+)$"),
    ("DEFINE", r"define\s+(?P<subject>.+)$"),
    ("EXPLAIN", r"explain\s+(?P<subject>.+)$"),
]


def extract_intent(prompt: str) -> str | None:
    """
    Extract a normalized intent key from a user prompt.

    The function lowercases and trims the incoming prompt, then tries each
    pattern in INTENT_PATTERNS in order. If a pattern matches, it captures
    the 'subject' group, normalizes whitespace, and returns a string in the
    form "<INTENT>:<subject>". If no pattern matches, the function returns
    None.

    Args:
        prompt: The incoming user prompt (raw string). This function will
            normalize case and surrounding whitespace.

    Returns:
        A normalized intent key (e.g. "DEFINE:artificial intelligence")
        when a known pattern matches, otherwise None.

    Examples:
        >>> extract_intent("what is AI")
        "DEFINE:ai"

        >>> extract_intent("explain neural networks")
        "EXPLAIN:neural networks"

        >>> extract_intent("tell me a joke")
        None
    """
    text = prompt.lower().strip()

    for intent, pattern in INTENT_PATTERNS:
        match = re.match(pattern, text)
        if not match:
            continue

        subject = match.group("subject").strip()
        subject = " ".join(subject.split())

        return f"{intent}:{subject}"

    return None


# print(extract_intent("what is AI"))
