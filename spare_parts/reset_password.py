
from fastapi import BackgroundTasks, HTTPException, Request

from sqlalchemy.orm import Session

from core.auth import auth
from core.mail import send_mail
from core.settings import settings

from schemas.auth import (
    EmailSchema,
    ResetPasswordDetails,
)

from v1.auth.views import get_user_by_email


def reset_password(
    email: str,
    bg_tasks: BackgroundTasks,
    request: Request,
):

    token = auth.encode_reset_token(email)

    emails = EmailSchema(
        emails=[email],
        body={
            "reset_link": f"{request.base_url}reset-password-confirm?token={token}",
            "company_name": settings.PROJECT_TITLE,
        },
    )

    send_mail(
        background_tasks=bg_tasks,
        subject=f"{settings.PROJECT_TITLE} Password Reset",
        emails=emails,
        template_name="reset_password.html",
    )

    return True


# ...

def reset_password_verification(
    body: ResetPasswordDetails,
    request: Request,
    bg_tasks: BackgroundTasks,
    db: Session
):

    email = auth.verify_reset_token(body.token)
    user = get_user_by_email(email, db)

    db.commit()

    # ...
    token = auth.encode_refresh_token(user.email)
    emails = EmailSchema(
        emails=[email],
        body={
            "reset_link": f"{request.base_url}reset-password-confirm?token={token}",
            "company_name": settings.PROJECT_TITLE,
        },
    )
    send_mail(
        background_tasks=bg_tasks,
        subject=f"{settings.PROJECT_TITLE} Password Reset",
        emails=emails,
        template_name="reset_password_confirmation.html",
    )

    return True
