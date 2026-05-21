import uuid


def generate_trace_id() -> str:
    """Generate uuid"""
    return uuid.uuid4().hex[:16]
