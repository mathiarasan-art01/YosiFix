"""JSON and dictionary serialization helpers."""
import json
from datetime import datetime, date

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)

def safe_dumps(data: any) -> str:
    """Serialize object safely into JSON string."""
    return json.dumps(data, cls=CustomJSONEncoder)

def safe_loads(text: str) -> any:
    """Safely parse JSON text."""
    try:
        return json.loads(text)
    except Exception:
        return {}
