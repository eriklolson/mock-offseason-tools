# utils/throttle.py

import time
from functools import wraps

def rate_limited(delay=0.5):
    """
    Decorator to throttle function calls by sleeping for `delay` seconds after each call.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            time.sleep(delay)
            return result
        return wrapper
    return decorator
