'''
BEFORE:

clean(prompt) -> lookup


AFTER:

clean(prompt) -> intent = extract_intent(prompt)

if intent:
    try semantic reuse
else:
    exact match only

# We are implementing :
1. Intent abstraction
2. Deterministic NLP heuristics
3. Risk-bounded design
4. Why embeddings are not magic
5. How real systems introduce intelligence gradually
6. This is far more valuable than jumping straight to vector DBs.

'''


def extract_intent(prompt:str) -> str | None:
    """
    Returns an intent key like:
    - DEFINE:ai
    - EXPLAIN:neural_network
    or None if intent is unknown
    """

    pass


