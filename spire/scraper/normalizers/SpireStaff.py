from typing import Optional


class SpireStaff:
    name: str
    email: Optional[str]

    def __init__(self, name: str, email=None):
        self.name = name.strip()
        self.email = email
