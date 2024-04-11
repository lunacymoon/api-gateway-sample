from enum import Enum
from enum import IntEnum as _IntEnum
from enum import unique

from .fastapi.exception import FastAPIError


class StrEnum(str, Enum):
    @classmethod
    def to_list(cls) -> list[str]:
        return [item.value for item in cls]


class IntEnum(_IntEnum):
    @classmethod
    def to_list(cls) -> list[str]:
        return [item.value for item in cls]


@unique
class ErrorCode(IntEnum):
    GENERAL_UNEXPECTED_ERROR = FastAPIError.code
    GENERAL_HTTP_SERVICE_ERROR = 1002
    GENERAL_REQUEST_VALIDATION_FAILED = 1003
    GENERAL_NOT_IMPLEMENTED = 1004
    GENERAL_UNAUTHORIZED = 1005
    SAGA_ORCHESTRATION_COMPENSATION_UNDONE = 1006
    GENERAL_RESOURCE_NOT_FOUND = 1007
    GENERAL_BAD_REQUEST = 1008

    # TODO: add service specific error code here
    # e.x.: ErrorCode.XXX01_API_RESPONSE_4XX_OR_5XX= 2001
