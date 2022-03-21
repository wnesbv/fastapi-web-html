
from fastapi import (
    BackgroundTasks,
    APIRouter,
    Depends,
    Request,
    Response,
    responses,
    Form,
    status,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from core.auth import auth
from core.dependency import get_db

from schemas.user import UserCreate
from schemas.auth import LoginDetails, ResetPasswordDetails

from v1.auth.views import create_user, login_user, get_user_by_email

from spare_parts.reset_password import reset_password, reset_password_verification


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):

    user_details = UserCreate(email=email, password=password)

    obj = create_user(
        user_details=user_details,
        background_tasks=background_tasks,
        request=request,
        db=db,
    )

    return responses.RedirectResponse(
        f"/user-detail/{obj.id}", status_code=status.HTTP_302_FOUND
    )


# ...

@router.get("/login")
def login_web(request: Request):
    return templates.TemplateResponse("auth/login.html",
        {"request": request}
    )


@router.post("/login")
async def login_web(
    bg_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):

    user_details = LoginDetails(
        email=email, password=password
    )
    response = responses.RedirectResponse(
        "/", status_code=status.HTTP_302_FOUND
    )

    response.token = login_user(
        user_details, db, bg_tasks, request, response=response
    )

    return response


# ...

@router.get("/reset-password/")
def to_reset_password(
    request: Request,
):

    return templates.TemplateResponse(
        "auth/reset-password.html",
        {"request": request},
    )


@router.post("/reset-password/")
async def to_reset_password(
    bg_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
):
    user = get_user_by_email(email, db)

    if user:
        reset_password(bg_tasks=bg_tasks, request=request, email=email)

        return templates.TemplateResponse(
            "components/successful.html",
            {
                "request": request,
                "message": "reset email sent..!",
            },
        )

    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "we don't have: email..!",
        },
    )


# ...

@router.get("/reset-password-confirm/")
def reset_password_confirm(
    request: Request,
):

    return templates.TemplateResponse(
        "auth/reset-password-confirm.html",
        {"request": request},
    )


@router.post("/reset-password-confirm/")
async def reset_password_confirm(
    token: str,
    bg_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    password: str = Form(...),
    re_password: str = Form(...),
):

    body = ResetPasswordDetails(token=token, password=password, re_password=re_password)

    email = auth.verify_reset_token(body.token)
    user = get_user_by_email(email, db)

    if body.password != body.re_password:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "message": "passwords aren't equal!..!",
            },
        )

    if auth.verify_password(body.password, user.password):
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "message": "It is not possible to use the same password as before..!",
            },
        )

    user.password = auth.hash_password(body.password)

    if user:
        reset_password_verification(body, request, bg_tasks, db)

        return templates.TemplateResponse(
            "components/successful.html",
            {
                "request": request,
                "message": "password reset successful..!",
            },
        )

    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "An error has occurred..!",
        },
    )
