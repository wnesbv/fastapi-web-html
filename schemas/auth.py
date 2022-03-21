
from typing import Any, Dict

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginDetails(BaseModel):
    email: str
    password: str

class RefreshDetails(BaseModel):
    refresh_token: str


# ...

class EmailSchema(BaseModel):
    emails: list[EmailStr]
    body: Dict[str, Any]


class ResetPasswordDetails(BaseModel):
    token: str
    password: str
    re_password: str
