
from fastapi import Request, Depends, HTTPException

from core.auth import auth
from core.dependency import get_db
from v1.utils import OAuth2PasswordBearerWithCookie

from models.mls.user import User
from schemas.user import UserOut, UserUpdate

from sqlalchemy.orm import Session


# ...
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl = "/")
# ...


def get_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):

    email = auth.decode_token(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "User doesn't exist")

    return user


def get_active_user(
    current_user: UserOut = Depends(get_user)
):
    if not current_user.email_verified:
        raise HTTPException(401, "Электронная почта не подтверждена!")
    if not current_user.is_active:
        raise HTTPException(401, "Этот аккаунт не активен!")

    return current_user


# ...

def update_user(
    id: int,
    user_details: UserUpdate,
    db: Session,
    current_user,
):

    existing_user = db.query(User).filter(User.id == current_user.id)

    user_details.__dict__.update()
    existing_user.update(user_details.__dict__)
    db.commit()

    return existing_user


# ...

def list_user(db: Session):

    obj_list = db.query(User).all()

    return obj_list


def retreive_user(id: int, db: Session):

    obj = db.query(User).filter(User.id == id).first()

    return obj
