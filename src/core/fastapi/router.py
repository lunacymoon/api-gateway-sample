from typing import Callable

from fastapi import Request, Response, status
from fastapi.routing import APIRoute as _APIRoute
from fastapi_utils.inferring_router import InferringRouter as _InferringRouter


class APIRoute(_APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        # NOTE: fix 204 response non-empty issue
        # https://github.com/tiangolo/fastapi/issues/717
        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            if response.status_code == status.HTTP_204_NO_CONTENT:
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            return response

        return custom_route_handler


class InferringRouter(_InferringRouter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, route_class=APIRoute)
