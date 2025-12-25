"""
AI Cache Phase 1 - FastAPI Application.

A FastAPI-based service that provides intelligent caching for LLM responses.
The service normalizes prompts, caches responses with TTL, performs intent-based
lookups, and enforces LRU eviction policies for memory efficiency.

Endpoints:
    POST /ask - Process a prompt and return a cached or freshly generated response
    GET /health - Health check endpoint
    GET /showcache - Display current cache contents
    GET /showprompts - Display prompt-to-entry mappings
    GET /showintents - Display intent-to-entry mappings
"""

from fastapi import FastAPI
from pydantic import BaseModel

from .core.cache import (get_from_cache, set_in_cache, show_cache,
                         show_intents_mapping, show_prompts_mapping)
from .policies.ttl import get_ttl
from .services.llm import generate_response

app = FastAPI(title="Evicta Phase 1")


class AskRequest(BaseModel):
    """Request model for the /ask endpoint.

    Attributes:
        prompt: The user's text prompt to process.
    """
    prompt: str


class AskResponse(BaseModel):
    """Response model for the /ask endpoint.

    Attributes:
        answer: The generated or cached response text.
        cache_hit: Boolean indicating if the response was served from cache (True)
                  or newly generated (False).
    """
    answer: str
    cache_hit: bool


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """
    Process a user prompt and return a cached or freshly generated response.

    Args:
        req: An AskRequest containing the user's prompt.

    Returns:
        An AskResponse with the answer and a cache_hit flag indicating whether
        the response was served from cache or newly generated.
    """
    prompt = req.prompt.strip()

    # Check cache
    cached_response = get_from_cache(prompt)
    if cached_response:
        return AskResponse(answer=cached_response, cache_hit=True)

    # Cache miss
    answer = generate_response(prompt)

    # Store in cache
    ttl_seconds = get_ttl()
    set_in_cache(prompt, answer, ttl_seconds)

    return AskResponse(answer=answer, cache_hit=False)


@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns:
        A dict with status "ok" to indicate the service is running.
    """
    return {"status": "ok"}


@app.get("/showcache")
def showcache():
    """
    Retrieve and display the entire cache.

    Returns:
        The cache_entries dictionary from the cache store.
    """
    return show_cache()


@app.get("/showprompts")
def showprompts():
    """
    Retrieve and display the prompt-to-entry mappings.

    Returns:
        A dict containing prompt_to_entry_id and entry_id_to_prompts mappings.
    """
    return show_prompts_mapping()


@app.get("/showintents")
def showintents():
    """
    Retrieve and display the intent-to-entry mappings.

    Returns:
        A dict containing intent_to_entry_id and entry_id_to_intents mappings.
    """
    return show_intents_mapping()
