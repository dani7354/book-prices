from dataclasses import dataclass


@dataclass
class ApiKey:
    id: int
    api_name: str
    api_user: str
    api_key: str

