from fastapi import FastAPI
from pydantic import BaseModel

from .core.cache import get_from_cache, set_in_cache, show_cache, show_prompts_mapping, show_intents_mapping
from .policies.ttl import get_ttl
from .services.llm import generate_response


app = FastAPI(title="AI Cache Phase 1")

class AskRequest(BaseModel):
    prompt: str

class AskResponse(BaseModel):
    answer: str
    cache_hit: bool

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    prompt = req.prompt.strip()

    # Check cache
    cached_response = get_from_cache(prompt)
    if cached_response:
        return AskResponse(answer=cached_response,cache_hit=True)

    # Cache miss 
    answer = generate_response(prompt)

    # Store in cache
    ttl_seconds = get_ttl(prompt)
    set_in_cache(prompt, answer, ttl_seconds)

    return AskResponse(answer=answer,cache_hit=False)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/showcache")
def show():
    return show_cache()

@app.get("/showprompts")
def show():
    return show_prompts_mapping()

@app.get("/showintents")
def show():
    return show_intents_mapping()