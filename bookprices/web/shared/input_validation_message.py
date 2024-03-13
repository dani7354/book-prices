def min_length_not_met(field_name: str, min_length: int) -> str:
    return f"{field_name} skal være mindst {min_length} tegn"


def max_length_exceeded(field_name: str, max_length: int) -> str:
    return f"{field_name} må maks. være {max_length} tegn"
