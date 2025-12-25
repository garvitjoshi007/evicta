import time
import unicodedata
from app.core import cache_store 
from app.semantic import intent

# Implementing LRU

def clean(prompt:str) -> str:
    # Remove Unicode "format" characters (e.g. zero-width space)
    prompt = "".join(
        ch for ch in prompt
        if unicodedata.category(ch) != "Cf"
    )

    # Normalize case and whitespace
    return " ".join(prompt.lower().split())
    

def get_from_cache(prompt:str) -> str | None :
    prompt = clean(prompt)

    hit = cache_store.get_entry_by_prompt(prompt)
    if hit:
        return hit

    intent_key = intent.extract_intent(prompt)
    if intent_key:
        entry_id = cache_store.intent_to_entry_id.get(intent)
        if entry_id:
            cache_store.associate_prompt_to_entry(prompt, entry_id)
            return cache_store.get_entry_by_prompt(prompt)
    return None


def set_in_cache(prompt: str, response: str, ttl_seconds: int) -> None:
    prompt = clean(prompt)

    # check if the prompt already points to an entry
    entry_id =  cache_store.get_entry_id_by_prompt(prompt)
    if entry_id is not None:
        cache_store.cache_entries[entry_id] = response
        cache_store.cache_entries['expires_at'] = time.time()+ttl_seconds
        cache_store.mru_update(entry_id)
        return

    # create new entry
    entry_id = cache_store.create_entry(response,ttl_seconds)
    cache_store.associate_prompt_to_entry(prompt , entry_id)

    # register intent if it exists
    intent_key = intent.extract_intent(prompt)
    if intent_key:
        cache_store.intent_to_entry_id[intent_key] = entry_id
        cache_store.associate_intent_to_entry(intent_key, entry_id)

    # enforce capacity limitations
    if len(cache_store.cache_entries) > cache_store.MAX_CACHE_SIZE:
        oldest_entry_id = next(iter(cache_store.cache_entries.keys()))
        cache_store._evict_entry(oldest_entry_id) 

def show_cache():
    return cache_store.cache_entries


def json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [json_safe(x) for x in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    return repr(obj)   # force any internal engine object to string


def show_prompts_mapping():
    return {
        "prompt_to_entry_id": json_safe(cache_store.prompt_to_entry_id),
        "entry_id_to_prompts": json_safe(cache_store.entry_id_to_prompts),
    }

def show_intents_mapping():
    return {
        "intent_to_entry_id": json_safe(cache_store.intent_to_entry_id),
        "entry_id_to_intents": json_safe(cache_store.entry_id_to_intents),
    }

