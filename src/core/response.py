from fastapi import status

from core.pydantic.model import BaseModel

from .enum import ErrorCode


class ErrorMessage(BaseModel):
    code: int
    message: str


class ValidationFailedMessage(BaseModel):
    code: int
    error_codes: list[int]


def response_400(subject: str) -> dict:
    return {
        status.HTTP_400_BAD_REQUEST: {
            'model': ErrorMessage,
            'description': f'{subject} bad request',
            'content': {
                'application/json': {
                    'example': {
                        'code': ErrorCode.GENERAL_BAD_REQUEST,
                        'deescription': '	Bad Request - The request could not be understood by the server due to malformed syntax. The message body will contain more information',
                        'message': 'bad request',
                    }
                }
            },
        }
    }


def response_404(subject: str) -> dict:
    return {
        status.HTTP_404_NOT_FOUND: {
            'model': ErrorMessage,
            'description': f'{subject} not found',
            'content': {
                'application/json': {
                    'example': {
                        'code': ErrorCode.GENERAL_RESOURCE_NOT_FOUND,
                        'message': 'resource not found',
                    }
                }
            },
        }
    }


def response_409() -> dict:
    return {
        status.HTTP_409_CONFLICT: {
            'model': ErrorMessage,
            'description': 'Conflict',
        }
    }


def response_422(subject: str) -> dict:
    return {
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            'model': ValidationFailedMessage,
            'description': f'{subject} validation failed',
            'content': {
                'application/json': {
                    'example': {
                        'code': ErrorCode.GENERAL_REQUEST_VALIDATION_FAILED,
                        'error_codes': [1, 2, 3],
                    }
                }
            },
        }
    }


def build_default_responses() -> dict:
    build_error_scheme = lambda *codes: {  # pylint: disable=unnecessary-lambda-assignment
        'content': {
            'application/json': {
                'schema': {
                    'required': ['code', 'message'],
                    'type': 'object',
                    'properties': {
                        'code': {
                            'title': 'Code',
                            'type': 'Integer',
                            'enum': codes,
                        },
                        'message': {
                            'title': 'Message',
                            'type': 'string',
                        },
                    },
                }
            }
        }
    }
    return {
        status.HTTP_400_BAD_REQUEST: build_error_scheme(
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
        status.HTTP_401_UNAUTHORIZED: build_error_scheme(
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
        status.HTTP_403_FORBIDDEN: build_error_scheme(
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
        status.HTTP_404_NOT_FOUND: build_error_scheme(
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
        status.HTTP_422_UNPROCESSABLE_ENTITY: build_error_scheme(
            ErrorCode.GENERAL_REQUEST_VALIDATION_FAILED,
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: build_error_scheme(
            ErrorCode.GENERAL_UNEXPECTED_ERROR,
            ErrorCode.GENERAL_HTTP_SERVICE_ERROR,
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
        status.HTTP_501_NOT_IMPLEMENTED: build_error_scheme(
            ErrorCode.GENERAL_NOT_IMPLEMENTED,
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
        status.HTTP_503_SERVICE_UNAVAILABLE: build_error_scheme(
            # add service specific error code here
            # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX,
        ),
    }
