from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from env import DISCORD_APP_ID, DISCORD_TOKEN, MIDDLEWARE_SECRET
from isabot.api.api import router as api_router
from isabot.api.battlenet.api import router as auth_router
from isabot.api.discord import base
from isabot.discord import commands


@asynccontextmanager
async def setup_app(app: FastAPI):
    """Setup app by registering the slash commands and other stuff"""
    await commands.register_slash_command(base.BASE, DISCORD_TOKEN, DISCORD_APP_ID)
    yield
    # clean up anything else before exiting app
    # ...


app = FastAPI(lifespan=setup_app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
)
app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_SECRET)
app.include_router(api_router)
app.include_router(auth_router)
