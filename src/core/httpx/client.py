from asgi_correlation_id.context import correlation_id
from httpx import AsyncClient, Limits

from settings import TIMEOUT_SECONDS

ASYNC_SESSION_PARAMS = {
    'limits': Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=TIMEOUT_SECONDS,
    ),
    'headers': {'X-Request-ID': str(correlation_id.get())},
    'timeout': TIMEOUT_SECONDS,
}


async def get_session():
    async with AsyncClient(**ASYNC_SESSION_PARAMS) as client:
        yield client
