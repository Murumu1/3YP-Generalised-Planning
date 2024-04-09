from functools import wraps


def non_negative(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, bool):
                continue
            elif isinstance(value, (int, float)):
                if value < 0:
                    raise ValueError(f"{key} in {function.__name__} should be non-negative")
        function(*args, **kwargs)
    return wrapper


def non_negative_and_non_zero(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, bool):
                continue
            elif isinstance(value, (int, float)):
                if value < 1:
                    raise ValueError(f"{key} in {function.__name__} should be non-negative and non-zero")
        function(*args, **kwargs)
    return wrapper
