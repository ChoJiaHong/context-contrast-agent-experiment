METHODS = ("direct", "generic_reframe", "context_contrast_single", "downward_loop", "upward_loop", "bidirectional_loop")

def get_executor(method: str):
    """Import an executor lazily so pure stopping rules stay dependency-light."""
    from importlib import import_module

    if method not in METHODS:
        raise ValueError(f"unknown method: {method}")
    return import_module(f"{__name__}.{method}").execute
