
from fastapi import APIRouter

from web.user import route_user
from web.vote import route_vote
from web.item import route_item
from web.auth import route_login
from web.trivia import route_trivia
from web.comment import route_comment

api_router = APIRouter()

api_router.include_router(route_user.router, prefix="", tags=["user-web"])
api_router.include_router(route_vote.router, prefix="", tags=["vote-web"])
api_router.include_router(route_item.router, prefix="", tags=["item-web"])
api_router.include_router(route_trivia.router, prefix="", tags=["trivia-web"])
api_router.include_router(route_login.router, prefix="", tags=["auth-web"])
api_router.include_router(route_comment.router, prefix="", tags=["comment-web"])
