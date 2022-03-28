
from datetime import datetime

import sqlalchemy as sa

from passlib.hash import pbkdf2_sha1

from starlette.requests import Request
from sqlalchemy.orm import declarative_base

from sqladmin import ModelAdmin


Base = declarative_base()


class User(Base):

    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    email = sa.Column(sa.String, index=True)
    username = sa.Column(sa.String, unique=True, index=True)
    password = sa.Column(sa.String)
    is_admin = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.id

    def get_display_name(self) -> str:
        return self.name or ""

    def get_id(self) -> int:
        assert self.id
        return self.id

    def get_hashed_password(self) -> str:
        return self.password or ""

    def get_scopes(self) -> list:
        return []


class AuthModelAdmin(ModelAdmin):
    def is_accessible(self, request: Request):

        token = request.cookies.get("session")
        if token:
            return True
        return False

    def is_visible(self, request: Request) -> bool:
        return True


class UserAdmin(AuthModelAdmin, model=User):
    column_list = [User.id, User.name]
    form_columns = [User.name, User.email, User.password, User.is_admin]
    column_details_list = [
        User.id,
        User.name,
        User.password,
    ]
    column_searchable_list = [User.id, User.name]
