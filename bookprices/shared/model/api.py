from dataclasses import dataclass


@dataclass
class ApiKey:
    id: int | None
    api_name: str
    api_user: str
    api_key: str

