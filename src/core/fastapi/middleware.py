import asyncio
from dataclasses import dataclass

from fastapi.logger import logger
from starlette import __version__ as starlette_version
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import Headers
from starlette.exceptions import ExceptionMiddleware as _ExceptionMiddleware
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .exception import FastAPIError
from .logging import http_context_var


class WrapperExceptionMiddleware(_ExceptionMiddleware):
    _version = '0.19.1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self._version != starlette_version:
            raise RuntimeError(
                f'Please update starlette.exceptions.ExceptionMiddleware.__call__ with version {starlette_version}'
            )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Error in exception_handlers, message cannot be printed after an async request. If need to print out the log,
        must add logger at the end of the try-catch block.

        e.x.:
            try:
                await self.app(scope, receive, sender)
            except Exception as exc:
                ...
                await response(scope, receive, sender)

                logger.warning(...)
        """

        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message['type'] == 'http.response.start':
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, sender)
        except Exception as exc:
            handler = None

            if isinstance(exc, HTTPException):
                handler = self._status_handlers.get(exc.status_code)

            if handler is None:
                handler = self._lookup_exception_handler(exc)

            if handler is None:
                raise exc

            if response_started:
                msg = 'Caught handled exception, but response already started.'
                raise RuntimeError(msg) from exc

            request = Request(scope, receive=receive)
            if asyncio.iscoroutinefunction(handler):
                response = await handler(request, exc)
            else:
                response = await run_in_threadpool(handler, request, exc)
            await response(scope, receive, sender)

            if isinstance(exc, (NotImplementedError, FastAPIError)):
                kwargs = {
                    'msg': f'{type(exc).__name__}: {exc}',
                    'exc_info': exc,
                }
                http_status = getattr(exc, 'http_status', -1)
                if http_status // 100 == 4:
                    logger.warning(**kwargs)
                elif http_status == 503:
                    logger.critical(**kwargs)
                else:
                    logger.error(**kwargs)


# https://github.com/encode/starlette/pull/1519#issuecomment-1060633787
@dataclass
class ParseRequestMiddleware:
    app: ASGIApp

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        # Ingest all body messages from the ASGI `receive` callable.
        chunks = await self.get_chunks(receive)
        headers = await self.get_headers(scope)
        http_context_var.set(
            {
                'request': {
                    'query_params': await self.get_params(scope),
                    'headers': dict(headers),
                    'body': await self.get_body(chunks, headers),
                },
            }
        )

        # Dispatch to the ASGI callable
        async def wrapped_receive():
            # First up we want to return any messages we've stashed.
            if chunks:
                return chunks.pop(0)
            # Once that's done we can just await any other messages.
            return await receive()

        await self.app(scope, wrapped_receive, send)

    @staticmethod
    async def get_chunks(receive: Receive) -> list[dict[str, bytes]]:
        more_body = True
        chunks: list[dict[str, bytes]] = []
        while more_body:
            message = await receive()
            more_body = message.get('more_body', False)
            chunks.append(message)

        return chunks

    @staticmethod
    async def get_params(scope: Scope) -> str:
        return scope['query_string'].decode('utf-8')

    @staticmethod
    async def get_headers(scope: Scope) -> Headers:
        return Headers(scope=scope)

    @staticmethod
    async def get_body(chunks: list[dict], headers) -> dict:
        stream: list[bytes] = [chunk.get('body', b'') for chunk in chunks]
        if stream[-1] != b'':
            stream.append(b'')  # Request.stream(), The last one is `b''`

        body: dict[str, str] = {}
        body['raw'] = str(b''.join(stream))[2:-1]  # 'b'abcde'' -> 'abcde'

        return body
