

from sqlalchemy.orm import Session

from models.mls.user import Like, Dislike
from schemas.vote import LikeDB, DislikeDB


def like_add(
    like_in: LikeDB,
    db: Session,
    like_user_id: int,
):

    new_like = Like(
        **like_in.dict(),
        like_user_id=like_user_id,
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return new_like


# ...

def dislike_add(
    dislike_in: DislikeDB,
    db: Session,
    dislike_user_id: int,
):

    new_dislike = Dislike(
        **dislike_in.dict(),
        dislike_user_id=dislike_user_id,
    )
    db.add(new_dislike)
    db.commit()
    db.refresh(new_dislike)

    return new_dislike


# ...

def retreive_like(
    id: int,
    db: Session,
    current_user,
):

    obj = db.query(Like).filter(
        Like.like_item_id == id,
        Like.like_user_id == current_user
    ).first()

    return obj


def retreive_dislike(
    id: int,
    db: Session,
    current_user,
):

    obj = db.query(Dislike).filter(
        Dislike.dislike_item_id == id,
        Dislike.dislike_user_id == current_user
    ).first()

    return obj
