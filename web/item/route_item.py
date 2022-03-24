
from fastapi import (
    HTTPException,
    APIRouter,
    Depends,
    Request,
    responses,
    Form,
    File,
    status,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from schemas.user import ItemCreate
from spare_parts.item import (
    list_item,
    list_user_item,
    retreive_item,
    update_item,
    item_delete,
    create_new_item,
)
from spare_parts.user import get_active_user
from core.dependency import get_db
from models.mls.user import User, Comment, Like, Dislike


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/create-item/")
def create_item(request: Request):
    return templates.TemplateResponse("item/create_item.html", {"request": request})


@router.post("/create-item/")
async def create_item(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
    title: str = Form(...),
    description: str = Form(...),
    image_url: str = File(...),
):

    item_in = ItemCreate(title=title, description=description, image_url=image_url)

    item = create_new_item(db=db, obj_in=item_in, owner_item_id=current_user.id)

    return responses.RedirectResponse(
        f"/item-detail/{ item.id }", status_code=status.HTTP_302_FOUND
    )


# ...

@router.get("/update-item/{id}")
def to_update_item(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
):

    obj = retreive_item(id=id, db=db)
    if obj.owner_item_id == current_user.id:

        return templates.TemplateResponse(
            "item/update.html",
            {
                "request": request,
                "id": id,
                "obj": obj,
            },
        )

    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "You are not permitted..!",
        },
    )


@router.post("/update-item/{id}")
async def to_update_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
    title: str = Form(...),
    description: str = Form(...),
    image_url: str = File(...),
):

    item = ItemCreate(
        title=title,
        description=description,
        image_url=image_url,
    )
    obj = update_item(
        id=id, item=item, db=db, owner_item_id=current_user.id
    ).first()

    return responses.RedirectResponse(
        f"/item-detail/{ obj.id }",
        status_code=status.HTTP_302_FOUND,
    )


# ...delete

@router.get("/list-item-delete/")
def list_item_delete(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
):
    obj_list = list_user_item(
        db, owner_item_id=current_user.id
    )

    return templates.TemplateResponse(
        "item/list_delete.html",
        {"request": request, "obj_list": obj_list}
    )


@router.get("/delete-item/{id}")
def delete_item(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    obj = retreive_item(id=id, db=db)

    return templates.TemplateResponse(
        "item/delete.html", {"request": request, "obj": obj}
    )


@router.post("/delete-item/{id}")
async def delete_item(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
):

    obj = retreive_item(id=id, db=db)

    if obj.owner_item_id == current_user.id or current_user.is_admin:

        item_delete(id=id, db=db, owner_item_id=current_user.id)

        return responses.RedirectResponse(
            "/list-item-delete/", status_code=status.HTTP_302_FOUND
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )


# ...list detail ...

@router.get("/item-list/")
def item_list(
    request: Request,
    db: Session = Depends(get_db),
    msg: str = None
):

    obj_list = list_item(db=db)

    return templates.TemplateResponse(
        "item/list.html", {"request": request, "obj_list": obj_list, "msg": msg}
    )


@router.get("/item-detail/{id}")
def item_detail(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):

    obj = retreive_item(id=id, db=db)
    cmt_list = db.query(Comment).filter(Comment.cmt_item_id == id)

    # ...
    obj_like = db.query(Like).filter(Like.like_item_id == id)
    total_like = obj_like.count()
    obj_dislike = db.query(Dislike).filter(Dislike.dislike_item_id == id)
    total_dislike = obj_dislike.count()

    return templates.TemplateResponse(
        "item/detail.html", {
        "request": request,
        "obj": obj,
        "cmt_list": cmt_list,
        "total_like": total_like,
        "total_dislike": total_dislike,
        }
    )
