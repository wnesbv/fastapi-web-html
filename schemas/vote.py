

from pydantic import BaseModel


class LikeBase(BaseModel):
    upvote: bool

class LikeChoose(LikeBase):
    like_item_id: int


class LikeDB(LikeBase):
    like_item_id: int
    like_user_id: int

    class Config:
        orm_mode=True


# ...

class DislikeBase(BaseModel):
    downvote: bool

class DislikeChoose(DislikeBase):
    dislike_item_id: int


class DislikeDB(DislikeBase):
    dislike_item_id: int
    dislike_user_id: int

    class Config:
        orm_mode=True
