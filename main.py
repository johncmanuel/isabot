from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from env import MIDDLEWARE_SECRET
from isabot.api.api import router as api_router
from isabot.api.handlers import handle_setup
from isabot.utils.client import http_client


@asynccontextmanager
async def setup_app(app: FastAPI):
    """Setup app by registering the slash commands and other stuff"""
    await http_client.start()
    await handle_setup()
    yield
    # clean up anything else before exiting app
    # ...
    await http_client.stop()


app = FastAPI(lifespan=setup_app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
)
app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_SECRET)
app.add_middleware(GZipMiddleware)
app.include_router(api_router)
