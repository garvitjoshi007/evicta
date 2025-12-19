from collections import OrderedDict
import time

cache_entries = OrderedDict() # authoritative -> Key: entry_id , Value: entry data
prompt_to_entry = {} # just for lookup -> Key: normalized prompt , Value: entry_id
entry_to_prompts = {} # for cleanups -> Key: entry_id , Value: set of prompts

_next_entry_id = 1
MAX_CACHE_SIZE = 10

def mru_update(entry_id: int) -> None:
    cache_entries.move_to_end(entry_id)
    return

def create_entry(response: str, ttl_seconds: int) -> int:
    global _next_entry_id
    entry_id = _next_entry_id
    _next_entry_id += 1
    cache_entries[entry_id] = {"response": response, "expires_at": time.time() + ttl_seconds}
    entry_to_prompts[entry_id] = set()
    return entry_id


def associate_prompt_to_entry(prompt: str, entry_id: int) -> None:
    # Remove prompt from old entry if it exists
    old_entry_id = prompt_to_entry.get(prompt)
    if old_entry_id:
        entry_to_prompts[old_entry_id].discard(prompt)

    # Add new mapping
    prompt_to_entry[prompt] = entry_id
    entry_to_prompts[entry_id].add(prompt)

    
def get_entry_id_by_prompt(prompt: str) -> int | None:
    return prompt_to_entry.get(prompt)

def get_entry_by_prompt(prompt: str) -> str | None:
    entry_id = prompt_to_entry.get(prompt)
    if entry_id is None:
        return None
    
    entry = cache_entries.get(entry_id)
    if entry is None:
        return None
    
    # check ttl
    if time.time() > entry['expires_at']:
        _evict_entry(entry_id)
        return None

    # update mru
    mru_update(entry_id)

    return entry.get('response')

def _evict_entry(entry_id: int):
    cache_entries.pop(entry_id, None)

    # for getting all prompts pointing to this entry
    prompts = entry_to_prompts.pop(entry_id,set())

    # remove prompt -> entry mapping
    for prompt in prompts:
        prompt_to_entry.pop(prompt)

    return

