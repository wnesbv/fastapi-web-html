
from fastapi import APIRouter, Request, Form, responses, status

from fastapi.params import Depends
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from schemas.vote import LikeChoose, DislikeChoose
from models.mls.user import User
from core.dependency import get_db

from spare_parts.user import get_active_user
from spare_parts.vote import like_add, dislike_add, retreive_like, retreive_dislike


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/like/{id}")
def like_create(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
):
    like_user_id=current_user.id
    if not retreive_like(
        current_user=like_user_id,
        id=id,
        db=db,
    ):

        return templates.TemplateResponse(
            "item/like.html",
            {"request": request},
        )

    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "have you already voted..!",
        },
    )


@router.post("/like/{id}")
def like_create(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
    upvote: bool = Form(True),
):
    item_in = LikeChoose(upvote=upvote, like_item_id=id)

    add_like = like_add(
        db=db,
        like_in=item_in,
        like_user_id=current_user.id
    )

    return responses.RedirectResponse(
        f"/item-detail/{add_like.like_item_id}", status_code=status.HTTP_302_FOUND
    )


# ...

@router.get("/dislike/{id}/")
def dislike_create(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
):
    dislike_user_id = current_user.id
    if not retreive_dislike(
        current_user=dislike_user_id,
        id=id,
        db=db
    ):

        return templates.TemplateResponse(
            "item/dislike.html",
            {"request": request},
        )

    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "have you already voted..!",
        },
    )


@router.post("/dislike/{id}/")
def dislike_create(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
    downvote: bool = Form(False),
):
    item_in = DislikeChoose(downvote=downvote, dislike_item_id=id)

    add_dislike = dislike_add(
        db=db,
        dislike_in=item_in,
        dislike_user_id=current_user.id
    )

    return responses.RedirectResponse(
        f"/item-detail/{add_dislike.dislike_item_id}",
        status_code=status.HTTP_302_FOUND
    )
