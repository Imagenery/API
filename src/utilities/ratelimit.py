from fastapi import FastAPI, Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from ..errors import APIException

limiter = Limiter(get_remote_address)


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    response = APIException(f"Rate Limit Exceeded: {exc.detail}", status_code=429).response()
    response = request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)
    return response


def init_limiter(app: FastAPI) -> None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
