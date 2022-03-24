
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from models.base import Base

from db_config.storage_config import engine
from db_config.utils import check_db_connected, check_db_disconnected

from web.base import api_router as web_app_router
from v1.api import api_router

from sqladmin import Admin
from sqladmin.mds.models import UserAdmin, ItemAdmin


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def include_router(app: FastAPI):
    app.include_router(api_router)
    app.include_router(web_app_router)

def create_db():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI()
    configure_static(app)
    include_router(app)
    create_db()
    return app


# ...

app = start_application()

# ...

admin = Admin(app, engine)
admin.register_model(UserAdmin)
admin.register_model(ItemAdmin)

# ...

@app.on_event("startup")
async def app_startup():
    await check_db_connected()


@app.on_event("shutdown")
async def app_shutdown():
    await check_db_disconnected()
