
from sqlalchemy.orm import Session

from models.mls.user import Comment
from schemas.comment import CommentCreate, CommentUpdate


def comment_new(
    obj_in: CommentCreate,
    db: Session,
    cmt_user_id: int,
):

    new_comment = Comment(
        **obj_in.dict(),
        cmt_user_id=cmt_user_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


def update_comment(
    id: int,
    cmt: CommentUpdate,
    db: Session,
    cmt_user_id,
):
    existing_cmt = db.query(Comment).filter(Comment.id == id)

    if not existing_cmt.first():
        return False

    cmt.__dict__.update(
        cmt_user_id=cmt_user_id
    )
    existing_cmt.update(cmt.__dict__)
    db.commit()

    return existing_cmt


def comment_delete(
    id: int,
    db: Session,
):

    existing_cmt = db.query(Comment).filter(Comment.id == id)

    if not existing_cmt.first():
        return False

    existing_cmt.delete(synchronize_session=False)
    db.commit()

    return existing_cmt


# ...

def retreive_cmt(
    id: int,
    db: Session
):

    obj = db.query(Comment).filter(Comment.id == id).first()

    return obj
