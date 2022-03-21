

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    name: str
    password: str

class UserOut(UserBase):
    id: int
    email_verified: bool
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


# ...

class ItemBase(BaseModel):
    title: str
    image_url: str | None = None
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_item_id: int

    class Config:
        orm_mode = True
