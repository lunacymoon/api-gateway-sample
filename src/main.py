from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.fastapi import FastAPI
from core.fastapi.exception import FastAPIError
from core.fastapi.middleware import ParseRequestMiddleware
from core.handler import (
    base_exception_handler,
    fastapi_exception_handler,
    http_exception_handler,
    not_implemented_exception_handler,
    request_validation_exception_handler,
)
from core.response import build_default_responses
from settings import API_DOCS, API_VERSION, APP_TITLE, APP_URL_VERSION, ORIGIN_REGEX
from settings.logging import DictConfigurator

_default_fastapi_parameters = {
    'title': APP_TITLE,
    'version': API_VERSION,
    'on_startup': [lambda: DictConfigurator().configure()],
    'responses': build_default_responses(),
}
if not API_DOCS:
    app = FastAPI(**_default_fastapi_parameters, openapi_url=None, docs=None, redoc_url=None)
else:
    app = FastAPI(**_default_fastapi_parameters)


app.add_middleware(ParseRequestMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(NotImplementedError, not_implemented_exception_handler)
app.add_exception_handler(FastAPIError, fastapi_exception_handler)
app.add_exception_handler(Exception, base_exception_handler)
app.add_versioning(APP_URL_VERSION)


app.add_api_route(
    '/',
    lambda: JSONResponse({'APP': APP_TITLE}),
    methods=['GET'],
    include_in_schema=False,
)
