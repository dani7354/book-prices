from dataclasses import dataclass


@dataclass(frozen=True)
class UserInfoViewModel:
    id: str
    email: str
    firstname: str
    lastname: str
    is_active: bool
    created: str
    updated: str
