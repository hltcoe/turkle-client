from typing import Optional

import pydantic


class User(pydantic.BaseModel):
    username: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    is_active: Optional[bool]
    is_staff: Optional[bool]
    is_superuser: Optional[bool]
