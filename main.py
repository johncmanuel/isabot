from fastapi import FastAPI

from env import DISCORD_APP_ID, DISCORD_TOKEN
from isabot.api.discord import register, setup
from isabot.discord.commands import register_slash_command

app = FastAPI()
app.include_router(setup.router)


@app.get("/")
async def root():
    return "Hello world"


@app.get("/register")
async def _register():
    if not DISCORD_TOKEN or not DISCORD_APP_ID:
        raise Exception("Env variables for discord token and/or app id are not set")
    await register_slash_command(register.REGISTER, DISCORD_TOKEN, DISCORD_APP_ID)
