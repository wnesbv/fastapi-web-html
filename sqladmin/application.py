
from typing import TYPE_CHECKING, List, Type, Union

import dataclasses
from dataclasses import dataclass

from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from passlib.context import CryptContext
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

from imia import (
    AuthenticationMiddleware,
    ImpersonationMiddleware,
    InMemoryProvider,
    LoginManager,
    SessionAuthenticator,
)
from core.settings import settings

admin_login = Jinja2Templates(directory="templates")
if TYPE_CHECKING:
    from sqladmin.models import ModelAdmin


__all__ = [
    "Admin",
]


@dataclass
class User:

    identifier: str = "details of the administrator@gmail.com"
    password: str = "$2b$12$gNUwKX24HyMiGxOsJTwloOVoY6pUDnL6PjnOZJSRLNDuv1LFvTfKW"

    scopes: list[str] = dataclasses.field(default_factory=list)

    # ...

    def get_display_name(self) -> str:
        return "User"

    def get_id(self) -> str:
        return self.identifier

    def get_hashed_password(self) -> str:
        return self.password

    def get_scopes(self) -> list:
        return self.scopes


secret_key = settings.SECRET_KEY

user_provider = InMemoryProvider(
    {
        "details of the administrator@gmail.com": User(scopes=["auth: impersonate_others"]),
        "customer@localhost": User(identifier="customer@localhost"),
    }
)

password_verifier = CryptContext(schemes=["bcrypt"])
login_manager = LoginManager(user_provider, password_verifier, secret_key)


async def login_view(request: Request) -> Response:
    msg = ""
    if "msg" in request.query_params:
        msg = "invalid credentials"

    if request.method == "POST":
        form = await request.form()
        email = form["email"]
        password = form["password"]

        user_token = await login_manager.login(request, email, password)
        if user_token:
            return RedirectResponse("/admin/app", status_code=302)
        return RedirectResponse(
            "/admin/login?msg=invalid_credentials", status_code=302
        )

    return admin_login.TemplateResponse(
        "auth/admin_login.html",
        {
            "request": request,
            "msg": msg,
        },
    )


async def logout_view(request: Request) -> RedirectResponse:

    if request.method == "POST":
        await login_manager.logout(request)

        return RedirectResponse("/admin/login", status_code=302)

    return RedirectResponse("/admin/app", status_code=302)


async def app_view(request: Request) -> HTMLResponse:

    user = request.auth.display_name

    return admin_login.TemplateResponse(
        "auth/logout_admin.html",
        {
            "request": request,
            "user": user,
        },
    )


# ...

class BaseAdmin:
    def __init__(
        self,
        app: Starlette,
        engine: Union[Engine, AsyncEngine],
        base_url: str = "/admin",
        title: str = "Admin",
        logo_url: str = None,
    ) -> None:
        self.app = app
        self.engine = engine
        self.base_url = base_url
        self._model_admins: List["ModelAdmin"] = []

        self.templates = Jinja2Templates("templates")
        self.templates.env.loader = ChoiceLoader(
            [
                FileSystemLoader("admin_templates"),
                PackageLoader("sqladmin", "admin_templates"),
            ]
        )
        self.templates.env.globals["min"] = min
        self.templates.env.globals["admin_title"] = title
        self.templates.env.globals["admin_logo_url"] = logo_url
        self.templates.env.globals["model_admins"] = self.model_admins

    @property
    def model_admins(self) -> List["ModelAdmin"]:
        return self._model_admins

    def _find_model_admin(self, identity: str) -> "ModelAdmin":
        for model_admin in self.model_admins:
            if model_admin.identity == identity:
                return model_admin

        raise HTTPException(status_code=404)

    def register_model(self, model: Type["ModelAdmin"]) -> None:

        model.engine = self.engine
        if isinstance(model.engine, Engine):
            model.sessionmaker = sessionmaker(bind=model.engine, class_=Session)
            model.async_engine = False
        else:
            model.sessionmaker = sessionmaker(bind=model.engine, class_=AsyncSession)
            model.async_engine = True

        self._model_admins.append((model()))


class BaseAdminView(BaseAdmin):
    async def _list(self, request: Request) -> None:
        model_admin = self._find_model_admin(request.path_params["identity"])
        if not model_admin.is_accessible(request):
            raise HTTPException(status_code=403)

    async def _create(self, request: Request) -> None:
        model_admin = self._find_model_admin(request.path_params["identity"])
        if not model_admin.can_create or not model_admin.is_accessible(request):
            raise HTTPException(status_code=403)

    async def _details(self, request: Request) -> None:
        model_admin = self._find_model_admin(request.path_params["identity"])
        if not model_admin.can_view_details or not model_admin.is_accessible(request):
            raise HTTPException(status_code=403)

    async def _delete(self, request: Request) -> None:
        model_admin = self._find_model_admin(request.path_params["identity"])
        if not model_admin.can_delete or not model_admin.is_accessible(request):
            raise HTTPException(status_code=403)

    async def _edit(self, request: Request) -> None:
        model_admin = self._find_model_admin(request.path_params["identity"])
        if not model_admin.can_edit or not model_admin.is_accessible(request):
            raise HTTPException(status_code=403)


class Admin(BaseAdminView):
    def __init__(
        self,
        app: Starlette,
        engine: Union[Engine, AsyncEngine],
        base_url: str = "/admin",
        title: str = "Admin",
        logo_url: str = None,
    ) -> None:

        assert isinstance(engine, (Engine, AsyncEngine))
        super().__init__(
            app=app, engine=engine, base_url=base_url, title=title, logo_url=logo_url
        )

        statics = StaticFiles(packages=["sqladmin"])

        def http_exception(request: Request, exc: Exception) -> Response:
            assert isinstance(exc, HTTPException)
            context = {
                "request": request,
                "status_code": exc.status_code,
                "message": exc.detail,
            }
            return self.templates.TemplateResponse(
                "error.html", context, status_code=exc.status_code
            )

        admin = Starlette(
            routes=[
                Mount("/statics", app=statics, name="statics"),
                Route("/", endpoint=self.index, name="index"),
                Route("/login", login_view, methods=["GET", "POST"]),
                Route("/logout", logout_view, methods=["POST"]),
                Route("/app", app_view),

                Route("/{identity}/list", endpoint=self.list, name="list"),
                Route(
                    "/{identity}/details/{pk}", endpoint=self.details, name="details"
                ),
                Route(
                    "/{identity}/delete/{pk}",
                    endpoint=self.delete,
                    name="delete",
                    methods=["DELETE"],
                ),
                Route(
                    "/{identity}/create",
                    endpoint=self.create,
                    name="create",
                    methods=["GET", "POST"],
                ),
                Route(
                    "/{identity}/edit/{pk}",
                    endpoint=self.edit,
                    name="edit",
                    methods=["GET", "POST"],
                ),
            ],
            exception_handlers={HTTPException: http_exception},

            # ...
            middleware=[
                Middleware(SessionMiddleware, secret_key=secret_key),
                Middleware(
                    AuthenticationMiddleware,
                    authenticators=[SessionAuthenticator(user_provider)],
                    on_failure="redirect",
                    redirect_to="/admin/login",
                    include_patterns=[r"\/app"],
                ),
                Middleware(ImpersonationMiddleware, user_provider=user_provider),
            ],
        )

        self.app.mount(base_url, app=admin, name="admin")

    async def index(self, request: Request) -> Response:
        return self.templates.TemplateResponse(
            "index.html", {"request": request}
        )

    async def list(self, request: Request) -> Response:
        await self._list(request)

        model_admin = self._find_model_admin(request.path_params["identity"])

        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pageSize", 0))
        search = request.query_params.get("search", None)
        sort_by = request.query_params.get("sortBy", None)
        sort = request.query_params.get("sort", None)

        pagination = await model_admin.list(page, page_size, search, sort_by, sort)
        pagination.add_pagination_urls(request.url)

        context = {
            "request": request,
            "model_admin": model_admin,
            "pagination": pagination,
        }

        return self.templates.TemplateResponse(model_admin.list_template, context)

    async def details(self, request: Request) -> Response:
        await self._details(request)

        model_admin = self._find_model_admin(request.path_params["identity"])

        model = await model_admin.get_model_by_pk(request.path_params["pk"])
        if not model:
            raise HTTPException(status_code=404)

        context = {
            "request": request,
            "model_admin": model_admin,
            "model": model,
            "title": model_admin.name,
        }

        return self.templates.TemplateResponse(model_admin.details_template, context)

    async def delete(self, request: Request) -> Response:
        await self._delete(request)

        identity = request.path_params["identity"]
        model_admin = self._find_model_admin(identity)

        model = await model_admin.get_model_by_pk(request.path_params["pk"])
        if not model:
            raise HTTPException(status_code=404)

        await model_admin.delete_model(model)

        return Response(content=request.url_for("admin:list", identity=identity))

    async def create(self, request: Request) -> Response:
        await self._create(request)

        identity = request.path_params["identity"]
        model_admin = self._find_model_admin(identity)

        Form = await model_admin.scaffold_form()
        form = Form(await request.form())

        context = {
            "request": request,
            "model_admin": model_admin,
            "form": form,
        }

        if request.method == "GET":
            return self.templates.TemplateResponse(model_admin.create_template, context)

        if not form.validate():
            return self.templates.TemplateResponse(
                model_admin.create_template,
                context,
                status_code=400,
            )

        model = model_admin.model(**form.data)
        await model_admin.insert_model(model)

        return RedirectResponse(
            request.url_for("admin:list", identity=identity),
            status_code=302,
        )

    async def edit(self, request: Request) -> Response:
        await self._edit(request)

        identity = request.path_params["identity"]
        model_admin = self._find_model_admin(identity)

        model = await model_admin.get_model_by_pk(request.path_params["pk"])
        if not model:
            raise HTTPException(status_code=404)

        Form = await model_admin.scaffold_form()
        context = {
            "request": request,
            "model_admin": model_admin,
        }

        if request.method == "GET":
            context["form"] = Form(obj=model)
            return self.templates.TemplateResponse(model_admin.edit_template, context)

        form = Form(await request.form())
        if not form.validate():
            context["form"] = form
            return self.templates.TemplateResponse(
                model_admin.edit_template,
                context,
                status_code=400,
            )

        await model_admin.update_model(pk=request.path_params["pk"], data=form.data)

        return RedirectResponse(
            request.url_for("admin:list", identity=identity),
            status_code=302,
        )
