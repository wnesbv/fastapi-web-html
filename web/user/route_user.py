
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form,
    responses,
    status,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from schemas.user import UserUpdate
from spare_parts.user import (
    update_user,
    list_user,
    retreive_user,
    get_active_user,
)

from models.mls.user import User

from core.auth import auth
from core.dependency import get_db


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/update-user/{id}")
def to_update(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
):

    obj = retreive_user(id=id, db=db)
    if obj.id == current_user.id or current_user.is_admin:

        return templates.TemplateResponse(
            "user/update.html",
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


@router.post("/update-user/{id}")
async def to_update(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_active_user),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):

    user_details = UserUpdate(
        name=name, email=email, password=auth.hash_password(password)
    )

    obj = update_user(
        id=id,
        user_details=user_details,
        current_user=current_user,
        db=db,
    ).first()

    return responses.RedirectResponse(
        f"/user-detail/{ obj.id }",
        status_code=status.HTTP_302_FOUND,
    )


# ...list detail ...

@router.get("/user-list/")
def user_list(
    request: Request,
    db: Session = Depends(get_db),
):

    obj_list = list_user(db=db)

    return templates.TemplateResponse(
        "user/list.html",
        {
            "request": request,
            "obj_list": obj_list,
        }
    )


@router.get("/user-detail/{id}")
def user_detail(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
):

    obj = retreive_user(id=id, db=db)

    return templates.TemplateResponse(
        "user/detail.html",
        {
            "request": request,
            "obj": obj,
        }
    )
