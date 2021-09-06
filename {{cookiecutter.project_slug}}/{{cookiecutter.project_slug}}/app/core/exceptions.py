import logging
from typing import Union, Type

from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from {{ cookiecutter.project_slug }}.processors import app


Exceptions = Union[HTTPException, Type[Exception], Exception, RequestValidationError]
_logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    error: str


async def handle_exception(status_code: int, message: str) -> JSONResponse:
    """ Return formatted response for received exception """

    return JSONResponse(content=dict(error=message), status_code=status_code)


@app.server.exception_handler(RequestValidationError)
async def validation(_: Request, exc: Exceptions):
    return await handle_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=exc.detail
    )


@app.server.exception_handler(Exception)
async def system(_: Request, exc: Exceptions):
    _logger.error(exc)
    return await handle_exception(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message='Internal server error'
    )


@app.server.exception_handler(HTTPException)
async def http(_: Request, exc: Exceptions):
    _logger.debug(exc)
    return await handle_exception(status_code=exc.status_code, message=exc.detail)
