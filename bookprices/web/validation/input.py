def length_equals_or_longer_than(value: str, min_length: int, allow_none=False) -> bool:
    if value is None:
        return allow_none
    return len(value.strip()) >= min_length


def length_equals_or_shorter_than(value: str, max_length: int, allow_none=False) -> bool:
    if value is None:
        return allow_none
    return len(value.strip()) <= max_length