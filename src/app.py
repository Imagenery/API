import os
from typing import Iterable

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute, Mount

from . import __version__
from .routes import image

app = FastAPI(title="Imagenery", version=__version__)
app.include_router(image.router)


# Root Endpoint


def get_endpoints(app: FastAPI | Mount) -> Iterable[tuple[str, str]]:
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.path not in ["/"]:  # Unwanted Routes
                yield (", ".join(list(route.methods)), route.path)


ENDPOINTS = [f"{methods}: {path}" for methods, path in get_endpoints(app)]


@app.get("/", include_in_schema=False)
async def root(request: Request):
    return {
        "message": "Welcome to the Imagenery API!",
        "version": app.version,
        "endpoints": ENDPOINTS,
        "code": 200,
    }


# Running
load_dotenv()

HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])


def dev():
    uvicorn.run("src.app:app", host=HOST, port=PORT, reload=True)


def start():
    uvicorn.run("src.app:app", host=HOST, port=PORT)
