

from pydantic import BaseModel


class CommentBase(BaseModel):
    opinion: str

class CommentCreate(CommentBase):
    cmt_item_id: int

class CommentUpdate(CommentBase):
    opinion: str


class CommentList(CommentBase):
    id: int
    cmt_user_id: int
    cmt_item_id: int

    class Config:
        orm_mode = True
