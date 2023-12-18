from contextlib import asynccontextmanager

from fastapi import FastAPI

from env import DISCORD_APP_ID, DISCORD_TOKEN
from isabot.api import api
from isabot.api.discord import base
from isabot.discord import commands

# from mangum import Mangum


@asynccontextmanager
async def setup_app(app: FastAPI):
    """Setup app by registering the slash commands and other stuff"""
    await commands.register_slash_command(base.BASE, DISCORD_TOKEN, DISCORD_APP_ID)
    yield
    # clean up anything else before exiting app
    # ...


app = FastAPI(lifespan=setup_app)
app.include_router(api.router)
# handler = Mangum(app)
