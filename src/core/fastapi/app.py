from collections import defaultdict

from fastapi import FastAPI as _FastAPI
from fastapi import __version__ as fastapi_version
from fastapi.middleware.asyncexitstack import AsyncExitStackMiddleware
from fastapi.routing import APIRoute
from fastapi_versioning.versioning import version_to_route
from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.types import ASGIApp

from .middleware import WrapperExceptionMiddleware


class FastAPI(_FastAPI):
    _version = '0.83.0'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self._version != fastapi_version:
            raise RuntimeError(f'Please update fastapi.FastAPI.build_middleware_stack with version {fastapi_version}')

    def build_middleware_stack(self) -> ASGIApp:
        debug = self.debug
        error_handler = None
        exception_handlers = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        # black
        # fmt: off
        # make sure the order of middleware is correct
        middleware = (
            [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug)]
            + self.user_middleware
            + [
                Middleware(
                    WrapperExceptionMiddleware, handlers=exception_handlers, debug=debug
                ),
                Middleware(AsyncExitStackMiddleware),
            ]
        )
        # fmt: on

        app = self.router
        for cls, options in reversed(middleware):
            app = cls(app=app, **options)
        return app

    # add versioning to FastAPI
    def add_versioning(
        self,
        default_version: tuple[int, int] = (1, 1),
        enable_latest: bool = False,
    ):
        version_route_mapping: dict[tuple[int, int], list[APIRoute]] = defaultdict(list)
        for route in self.routes:
            version, route = version_to_route(route, default_version)
            version_route_mapping[version].append(route)

        versions = sorted(version_route_mapping.keys())
        for version in versions:
            major, minor = version
            prefix = f'/v{major}_{minor}' if minor != 0 else f'/v{major}'
            versioned_app = FastAPI(routes=None, **vars(self))
            for route in version_route_mapping[version]:
                versioned_app.router.routes.append(route)
                if route.path not in [
                    self.openapi_url,
                    self.docs_url,
                    self.redoc_url,
                    self.swagger_ui_oauth2_redirect_url,
                ]:
                    self.routes.remove(route)
            self.mount(prefix, versioned_app)

            # pylint: disable=cell-var-from-loop
            @self.get(
                f'{prefix}/docs',
                tags=['Docs'],
                name=f'v{major}.{minor}',
                description=f'ECIP API `{prefix}` OpenAPI document',
                status_code=302,
            )
            def func() -> None:
                pass
