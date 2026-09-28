from dataclasses import dataclass
from typing import Optional
@dataclass
class User:
    id: int
    name: str
    role: str
def get_users() -> list[User]:
    return [
        User(1, "Jack", "AI Engineer"),
        User(2, "Tom", "Backend Engineer"),
    ]
def find_user_name(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Jack"

    return None
def get_user_names() -> list[str]:
    return ["Jack", "Tom", "Alice"]
def get_user() -> dict[str, str]:
    return {
        "name": "Jack",
        "role": "AI Engineer",
    }