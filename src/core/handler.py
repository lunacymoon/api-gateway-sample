from typing import Union

from fastapi import Request, status
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.pydantic.field import Int32
from core.pydantic.model import BaseModel

from .enum import ErrorCode
from .exception import BaseException_
from .fastapi.exception import FastAPIError


class ExceptionResponseContent(BaseModel):
    message: str = 'internal server error'
    code: Int32 = ErrorCode.GENERAL_UNEXPECTED_ERROR
    data: Union[dict, list, None]


async def base_exception_handler(_: Request, exp: Union[Exception, None]):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ExceptionResponseContent(
            message=BaseException_.message,
            code=BaseException_.code,
        ).dict(),
    )


async def http_exception_handler(
    _: Request,
    exp: Union[FastAPIHTTPException, StarletteHTTPException],
):
    return JSONResponse(
        status_code=exp.status_code,
        content=ExceptionResponseContent(
            message=exp.detail,
            code=ErrorCode.GENERAL_HTTP_SERVICE_ERROR,
        ).dict(),
    )


async def request_validation_exception_handler(_: Request, exp: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ExceptionResponseContent(
            message=str(exp),
            code=ErrorCode.GENERAL_REQUEST_VALIDATION_FAILED,
        ).dict(),
    )


async def not_implemented_exception_handler(_: Request, exp: NotImplementedError):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content=ExceptionResponseContent(
            message='Not Implemented',
            code=ErrorCode.GENERAL_NOT_IMPLEMENTED,
        ).dict(),
    )


async def fastapi_exception_handler(_: Request, exp: FastAPIError):
    return JSONResponse(
        status_code=exp.http_status,
        content=ExceptionResponseContent(
            message=exp.message,
            code=exp.code,
            data=exp.data,
        ).dict(),
    )


# TODO: add service specific exception handler below
