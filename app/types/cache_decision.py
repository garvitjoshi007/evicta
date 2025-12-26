from dataclasses import dataclass
from enum import Enum

class HitType(str, Enum):
    EXACT = "exact"
    INTENT = "intent"
    SEMANTIC = "semantic"
    MISS = "miss"

@dataclass(frozen=True)
class CacheDecision:
    hit_type: HitType
    entry_id: str | None
    ttl_remaining: float
    confidence: float
