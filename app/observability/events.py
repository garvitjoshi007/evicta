import time
import json
import uuid
from typing import Any, Dict

def emit(event_type: str, payload: Dict[str, Any]) -> None:
    request_id = uuid.uuid4().hex[:8]
    event = {
        "request_id": request_id,
        "event": event_type,
        "timestamp": time.ctime(),
        **payload,
    }
    print(json.dumps(event, ensure_ascii=False))