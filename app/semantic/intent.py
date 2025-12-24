'''
BEFORE:

clean(prompt) -> lookup


AFTER:

prompt = clean(prompt)

1. Try prompt_to_entry lookup
2. If miss → extract intent
3. If intent exists → try intent_to_entry lookup
4. If found → return entry (and bind this prompt to it)
5. Else → miss

'''

import re

INTENT_PATTERNS = [
    ("DEFINE", r'(?:what is|what\'s)\s+(?P<subject>.+)$'),
    ("DEFINE", r'define\s+(?P<subject>.+)$'),
    ("EXPLAIN", r'explain\s+(?P<subject>.+)$'),
]

def extract_intent(prompt: str) -> str | None:
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


