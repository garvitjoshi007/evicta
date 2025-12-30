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
from app.types.cache_decision import IntentResult

INTENT_PATTERNS = [
    ("DefineConcept",
     r"^(what is|what's|define|meaning of)\s+(?P<subject>.+)$"),

    ("ExplainConcept",
     r"^(explain)\s+(?P<subject>.+)$"),

    ("DifferenceBetween",
     r"^(difference between|compare)\s+(?P<a>.+?)\s+(and|vs|versus)\s+(?P<b>.+)$"),

    ("HowToGuide",
     r"^(how to|steps to|guide to|procedure to)\s+(?P<subject>.+)$"),

    ("TroubleshootIssue", [
        r"^(?P<subject>.+?)\s+(error|not working|failed|exception|issue|problem)$",
        r"^(error|not working|failed|exception|issue|problem)\s+(?P<subject>.+)$",
    ]),

    ("WriteCode",
     r"^(write code|write|implement)\s+(?P<subject>.+)$"),

    ("DebugError",
     r"^(?P<subject>traceback|stack trace|segfault|panic|exception)"
     r"(?:\s+in\s+(?P<context>.+))?$"),

    ("CreativeGeneration",
     r"^(write|create)\s+(a\s+)?(?P<subject>story|poem|caption|lyrics|dialogue)"
     r"(?:\s+about\s+(?P<context>.+))?$"),

    ("FindResource",
     r"^(find|search|link|resource|course)\s+(for\s+)?(?P<subject>.+)$"),

    ("InstallSetup",
     r"^(install|setup|configure|download)\s+(?P<subject>.+)$"),

    ("ToolRecommendation",
     r"^(which|best|better|recommend|suggest)\s+(?P<subject>.+)$"),

    ("SummarizeText",
     r"^(summarize|rewrite|paraphrase|shorten|simplify|translate)\s+(?P<subject>.+)$"),
]


INTENT_BASE_CONFIDENCE = {
    "DifferenceBetween": 0.95,
    "InstallSetup": 0.90,
    "HowToGuide": 0.88,
    "DefineConcept": 0.85,
    "ExplainConcept": 0.80,
    "WriteCode": 0.85,
    "DebugError": 0.90,
    "TroubleshootIssue": 0.70,
    "FindResource": 0.65,
    "CreativeGeneration": 0.75,
    "SummarizeText": 0.85,
}

NOISE_PATTERNS = {
    "DefineConcept": [
        r"\bmeaning\b",
        r"\boverview\b",
        r"\bbasics\b",
        r"\bin simple terms\b",
        r"\bwith example(s)?\b",
    ],
    "ExplainConcept": [
        r"\bin simple terms\b",
        r"\bwith example(s)?\b",
    ],
    "SummarizeText": [
        r"\bin simple words\b",
        r"\bshort\b",
    ],
    "InstallSetup": [
        r"\bon ubuntu\b",
        r"\bon linux\b",
        r"\bon mac(os)?\b",
        r"\bon windows\b",
    ],
}


NOISE_PENALTY = 0.05

def normalize_subject(intent:str,subject:str) -> tuple[str,bool]:
    """
    Returns (normalized_subject, noise_removed)
    """

    noise_removed = False
    patterns = NOISE_PATTERNS.get(intent, [])

    for pat in patterns:
        new_subject, count = re.subn(pat,"",subject)
        if count > 0:
            noise_removed = True
            subject = new_subject

    subject = " ".join(subject.split())
    return subject, noise_removed
        


def canonical_pair(a: str, b: str) -> str:
    a = " ".join(a.split())
    b = " ".join(b.split())
    return " ".join(sorted([a, b]))

def extract_intent(prompt: str) -> IntentResult | None:
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

    for intent, patterns in INTENT_PATTERNS:
        if isinstance(patterns, str):
            patterns = [patterns]

        for pattern in patterns:
            match = re.match(pattern, text)
            if not match:
                continue

            g = match.groupdict()

            if intent == "DifferenceBetween":
                subject = canonical_pair(g["a"], g["b"])

            elif intent == "DebugError":
                subject = g["subject"]
                if g.get("context"):
                    subject += f" {g['context']}"

            elif intent == "CreativeGeneration":
                subject = g["subject"]
                if g.get("context"):
                    subject += f" about {g['context']}"

            else:
                subject = g.get("subject", "")

            subject = " ".join(subject.split())
            subject, noise_removed = normalize_subject(intent, subject)

            confidence = compute_confidence(intent=intent,subject=subject,pattern=pattern,noise_removed=noise_removed)
            return IntentResult(
                intent=intent,
                subject=subject,
                confidence=confidence,
                source="rule"
            )

    return None


def subject_specificity(subject: str) -> float:
    tokens = subject.split()
    n = len(tokens)

    generic_subjects = {"it", "this", "that", "something", "error", "issue"}

    if subject in generic_subjects:
        return 0.4

    return min(1.0, 0.6+(0.1*n))


def pattern_strength(pattern:str):
    if len(pattern) > 70:
        return 1.0
    if len(pattern) > 40:
        return 0.9
    return 0.8


def compute_confidence(intent, subject, pattern, noise_removed):
    score = INTENT_BASE_CONFIDENCE.get(intent, 0.7)

    score *= subject_specificity(subject)
    score *= pattern_strength(pattern)

    if noise_removed:
        score -= NOISE_PENALTY

    return round(max(0.0, min(score, 1.0)), 2)
    

# print(extract_intent("what is AI"))
