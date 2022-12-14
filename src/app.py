import os
from typing import Iterable

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute, Mount

from . import __version__
from .errors import APIException
from .routes import image
from .utilities import init_limiter

app = FastAPI(title="Imagenery", version=__version__)
init_limiter(app)
app.include_router(image.router)

# Error Handlers


@app.exception_handler(APIException)
async def api_exception(_request: Request, exception: APIException):
    return exception.response()


@app.exception_handler(404)
async def not_found(_request: Request, exception: Exception):
    return APIException("Not Found", status_code=404).response()


@app.exception_handler(500)
async def internal_server_error(_request: Request, exception: Exception):
    return APIException(f"{str(exception)}", status_code=404).response()


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
