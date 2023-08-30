from dataclasses import dataclass, field


@dataclass
class Credentials:
    user_email: str = field(init=True, repr=False)
    user_uid: str
    api_key: str
