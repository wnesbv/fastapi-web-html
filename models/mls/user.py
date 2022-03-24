
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from db_config.storage_config import Base



class User(Base):
    __tablename__ = "user_u"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True, unique=True,)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ...
    user_item = relationship("Item", back_populates="item_user")

    user_cmt = relationship("Comment", back_populates="cmt_user")

    user_like = relationship("Like", back_populates="like_user")
    user_dislike = relationship("Dislike", back_populates="dislike_user")

    def __str__(self):
        return str(self.name)


class Item(Base):
    __tablename__ = "item_t"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # ...
    owner_item_id = Column(Integer, ForeignKey("user_u.id"))

    # ...
    item_user = relationship("User", back_populates="user_item")

    item_cmt = relationship("Comment", back_populates="cmt_item")

    item_like = relationship("Like", back_populates="like_item")
    item_dislike = relationship("Dislike", back_populates="dislike_item")

    def __str__(self):
        return self.id


class Comment(Base):
    __tablename__ = "comment_c"

    id = Column(Integer, nullable=False, primary_key=True)
    opinion = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cmt_user_id = Column(Integer, ForeignKey("user_u.id"))
    cmt_item_id = Column(Integer, ForeignKey("item_t.id"))

    # ...
    cmt_user = relationship("User", back_populates="user_cmt")
    cmt_item = relationship("Item", back_populates="item_cmt")

    def __str__(self):
        return self.id


# ...

class Like(Base):
    __tablename__ = "like_l"

    upvote = Column(Boolean, nullable=True)

    like_user_id = Column(Integer, ForeignKey("user_u.id"), primary_key=True)
    like_item_id = Column(Integer, ForeignKey("item_t.id"), primary_key=True)

    # ...
    like_user = relationship("User", back_populates="user_like")
    like_item = relationship("Item", back_populates="item_like")

    def __str__(self):
        return str(self.like_user_id)


class Dislike(Base):
    __tablename__ = "dislike_d"

    downvote = Column(Boolean, nullable=True)

    dislike_user_id = Column(Integer, ForeignKey("user_u.id"), primary_key=True)
    dislike_item_id = Column(Integer, ForeignKey("item_t.id"), primary_key=True)

    # ...
    dislike_user = relationship("User", back_populates="user_dislike")
    dislike_item = relationship("Item", back_populates="item_dislike")

    def __str__(self):
        return str(self.dislike_user_id)
