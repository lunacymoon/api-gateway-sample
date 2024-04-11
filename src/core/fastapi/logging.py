import os
import sys
from contextvars import ContextVar
from logging import Filter, LogRecord, getLogger
from typing import Optional

http_context_var: ContextVar[Optional[dict]] = ContextVar('http_context_var', default=None)
FastAPILogger = getLogger('fastapi')


class HTTPFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        info: dict = http_context_var.get() or {}
        for k, v in info.items():
            setattr(record, k, v)

        return True


class ASGIExceptionFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        setattr(record, 'origin_msg', record.msg)
        if str(record.msg).strip() == 'Exception in ASGI application' and record.exc_info:
            try:
                _, error, _ = record.exc_info
                record.msg = f'{type(error).__name__}: {str(error)}'
            except Exception:
                pass

        return True


class RelativePathFilter(Filter):
    def filter(self, record):
        pathname = record.pathname
        record.relativepath = None
        abs_sys_paths = map(os.path.abspath, sys.path)
        for path in sorted(abs_sys_paths, key=len, reverse=True):  # longer paths first
            if not path.endswith(os.sep):
                path += os.sep
            if pathname.startswith(path):
                record.relativepath = os.path.relpath(pathname, path)
                break
        else:
            record.relativepath = os.path.relpath(pathname, path)

        return True
