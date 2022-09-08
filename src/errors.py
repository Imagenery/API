from typing import Any, Dict

from fastapi.responses import JSONResponse

from . import __version__


class APIException(Exception):
    def __init__(self, detail: str, status_code: int = 500, headers: Dict[str, Any] | None = None) -> None:
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

    def response(self) -> JSONResponse:
        return JSONResponse(
            content={"detail": self.detail, "version": __version__, "code": self.status_code},
            status_code=self.status_code,
            headers=self.headers,
        )
