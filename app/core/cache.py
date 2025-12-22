import time
import unicodedata
from app.core import cache_store 

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
    return cache_store.get_entry_by_prompt(prompt)

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
    else:
        entry_id = cache_store.create_entry(response,ttl_seconds)
        cache_store.associate_prompt_to_entry(prompt , entry_id)

        # enforce capacity limitations
        if len(cache_store.cache_entries) > cache_store.MAX_CACHE_SIZE:
            oldest_entry_id = next(iter(cache_store.cache_entries.keys()))
            cache_store._evict_entry(oldest_entry_id) 

def show_cache():
    return cache_store.cache_entries






