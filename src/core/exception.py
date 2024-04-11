from fastapi import status

from .enum import ErrorCode
from .fastapi.exception import FastAPIError


class BaseException_(FastAPIError):
    code = ErrorCode.GENERAL_UNEXPECTED_ERROR


class ValidationFailedException(FastAPIError):
    def __init__(self, message: str):
        super().__init__(
            code=ErrorCode.GENERAL_REQUEST_VALIDATION_FAILED,
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
        )


# TODO: add service specific exception below
