from dataclasses import dataclass, asdict

@dataclass
class Metrics:
    total_decisions: int = 0
    exact_hits: int = 0
    intent_hits: int = 0
    cache_misses: int = 0
    cache_expired: int = 0
    cache_evicted: int = 0

    def snapshot(self) -> dict:
    # Return a safe, read-only view
        return asdict(self)

METRICS = Metrics()