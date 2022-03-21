
from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from schemas.user import UserOut
from spare_parts.item import search_item
from spare_parts.user import get_active_user, list_user
from core.dependency import get_db


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/search/")
def autocomplete(
    request: Request,
    query: str | None = None,
    db: Session = Depends(get_db)
):

    obj_list = search_item(query, db=db)

    return templates.TemplateResponse(
        "components/search.html",
        {"request": request, "obj_list": obj_list}
    )


# ...

@router.get("/")
async def home(
    request: Request,
    db: Session = Depends(get_db),
    msg: str = None
):

    obj_list = list_user(db=db)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "obj_list": obj_list, "msg": msg}
    )


@router.get("/me/", response_model=UserOut)
def get_user_profile(current_user: UserOut = Depends(get_active_user)):
    return current_user
