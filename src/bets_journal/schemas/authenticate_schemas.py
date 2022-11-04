from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str

class UserPost(UserBase):
    password: str


class UserDB(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


