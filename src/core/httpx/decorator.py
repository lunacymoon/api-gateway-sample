import functools
from json import JSONDecodeError
from typing import Callable, Optional, Union

from fastapi import status
from httpx import HTTPError, Request, Response

from settings import IS_DEBUG, IS_LOCAL_ENV

from ..fastapi import FastAPILogger


def get_headers(input_: Union[Request, Response]) -> dict:
    return dict(input_.headers)


def get_body(input_: Union[Request, Response]) -> Optional[Union[dict, str]]:
    body: dict[str, str] = {}
    body['raw'] = str(input_.content)

    return body


def http_error_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        class_ = args[0]

        # FIXME
        # assert inspect.isclass(class_ := args[0]), args[0]
        try:
            return await func(*args, **kwargs)
        except HTTPError as e:
            response = getattr(e, 'response', None)
            extra = {
                'request': {
                    'method': str(e.request.method),
                    'url': str(e.request.url),
                    'headers': get_headers(e.request),
                    'body': get_body(e.request),
                },
                'response': {
                    'status_code': response.status_code,
                    'headers': get_headers(response),
                    'body': get_body(response),
                }
                if response
                else {},
            }
            FastAPILogger.warning(
                f'{func.__qualname__}.{type(e).__name__}: {response.text if response else str(e)}',
                extra=extra,
            )
            if IS_DEBUG and IS_LOCAL_ENV:
                import devtools  # pylint: disable=import-outside-toplevel

                devtools.debug(extra)

            extra_data = {}
            if not response or response.status_code // 100 == 5:
                http_status = status.HTTP_503_SERVICE_UNAVAILABLE
                msg = f'{class_.__service_name__} service unavailable'
            else:
                http_status = response.status_code
                try:
                    reponse_data = response.json()
                    msg = f'{reponse_data.get("message", "")} ({reponse_data.get("code", "") or reponse_data.get("error_code", "")})'
                    extra_data = reponse_data.get('data', {})
                except JSONDecodeError as parser_err:
                    FastAPILogger.critical(f'Parsing response failed, {parser_err}')
                    msg = response.text

            raise class_.__exception__(msg, http_status=http_status, data=extra_data)

    return wrapper
