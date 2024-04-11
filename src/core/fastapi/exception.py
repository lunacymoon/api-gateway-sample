from fastapi import status
from fastapi.exceptions import FastAPIError as _FastAPIError


class FastAPIError(_FastAPIError):
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = 1001
    message = 'Unexpected'
    data = {}

    def __init__(self, msg=None, **kwargs):
        if msg:
            self.message = msg
        for k, v in kwargs.items():
            setattr(self, k, v)

        super().__init__(self.message)

    def __repr__(self):
        return f'{self.__class__.__name__}:CODE={self.code},MESSAGE={self.message}'
