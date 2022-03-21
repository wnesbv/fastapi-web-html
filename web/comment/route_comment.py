
from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Form,
    responses,
)

from fastapi.params import Depends
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from schemas.comment import CommentCreate, CommentUpdate
from models.mls.user import User
from core.dependency import get_db

from spare_parts.user import get_active_user
from spare_parts.comment import (
    comment_new,
    update_comment,
    retreive_cmt,
    comment_delete,
)


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.post("/item-detail/{id}/")
def create_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
    opinion: str = Form(...),
):

    comment = CommentCreate(opinion=opinion, cmt_item_id=id)
    obj = comment_new(
        db=db,
        obj_in=comment,
        cmt_user_id=current_user.id,
    )

    return responses.RedirectResponse(
        f"/item-detail/{obj.cmt_item_id}", status_code=status.HTTP_302_FOUND
    )


# ...

@router.get("/update-comment/{id}/")
def up_comment(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
):
    cmt_user_id = current_user.id
    cmt = retreive_cmt(id=id, db=db)

    return templates.TemplateResponse(
        "item/up_comment.html",
        {"request": request, "id": id, "cmt_user_id": cmt_user_id, "cmt": cmt},
    )


@router.post("/update-comment/{id}/")
async def up_comment(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
    opinion: str = Form(...),
):

    cmt = CommentUpdate(
        opinion=opinion,
    )
    obj = update_comment(id=id, cmt=cmt, db=db, cmt_user_id=current_user.id).first()

    return responses.RedirectResponse(
        f"/item-detail/{obj.id}", status_code=status.HTTP_302_FOUND
    )


@router.get("/delete-comment/{id}")
def delete_comment(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_active_user),
):

    cmt_user_id = current_user.id
    obj = retreive_cmt(id=id, db=db)
    return templates.TemplateResponse(
        "item/delete.html", {"request": request, "cmt_user_id": cmt_user_id, "obj": obj}
    )


@router.post("/delete-comment/{id}")
def delete_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_active_user),
):
    obj = retreive_cmt(id=id, db=db)

    if obj.cmt_user_id == current_user.id or current_user.is_admin:
        comment_delete(id=id, db=db)

        return responses.RedirectResponse(
            "/item-list/", status_code=status.HTTP_302_FOUND
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )
