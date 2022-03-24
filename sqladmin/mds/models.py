
from sqladmin import ModelAdmin
from starlette.requests import Request
from models.mls.user import User, Item


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
    form_columns = [User.name, User.email]
    column_details_list = [
        User.id,
        User.name,
    ]
    column_searchable_list = [User.id, User.name]


class ItemAdmin(AuthModelAdmin, model=Item):
    create_template = "custom_create.html"
    edit_template = "custom_edit.html"
    # ...
    column_list = [Item.id, Item.title, Item.owner_item_id]
    form_columns = [Item.title, Item.description]
    column_details_list = [Item.id, Item.title, Item.owner_item_id, Item.description]
    column_searchable_list = [Item.id, Item.title, Item.owner_item_id]
