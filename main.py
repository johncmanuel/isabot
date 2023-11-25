from fastapi import FastAPI

from isabot.api import api
from isabot.api.discord import register, setup
from isabot.discord.commands import register_slash_command

app = FastAPI()
app.include_router(setup.router)
app.include_router(api.router)
