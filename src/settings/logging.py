import urllib
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, getLevelName, getLogger
from logging.config import DictConfigurator as _DictConfigurator

import click
import gunicorn.glogging
import uvicorn.protocols.utils
import yaml
from pythonjsonlogger.jsonlogger import JsonFormatter as _JsonFormatter
from uvicorn.logging import AccessFormatter, ColourizedFormatter, DefaultFormatter

from . import IS_DEBUG, IS_LOCAL_ENV, LOGGING_CONFIG_FILE


def http_status_code_to_log_level(code: int) -> int:
    return {1: INFO, 2: INFO, 3: INFO, 4: WARNING, 5: ERROR}[int(code / 100)]


def overwride_get_path_with_query_string(scope) -> str:
    """
    Fix scope['path'] to scope['raw_path'], Because `scope.path` will ignore the `path` of mount

    origin_app.mount('v1', versioned_app)
        origin_message: 'GET /abc?test=true HTTP/1.1' 200 OK
        fixed_message:  'GET /v1/abc?test=true HTTP/1.1' 200 OK
    """

    path_with_query_string = urllib.parse.quote(scope['raw_path'].decode())
    if scope['query_string']:
        path_with_query_string = f'{path_with_query_string}?{scope["query_string"].decode("ascii")}'

    return path_with_query_string


class DictConfigurator(_DictConfigurator):
    def __init__(self):
        # To start Uvicorn from the command line, the --log-format parameter must be set to preload the source code to complete the Monkey-Patch
        uvicorn.protocols.utils.get_path_with_query_string = overwride_get_path_with_query_string

        with open(LOGGING_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            if not IS_LOCAL_ENV:
                for handler in config['handlers']:
                    config['handlers'][handler]['formatter'] = 'json'
            if IS_DEBUG:
                for logger in config['loggers']:
                    config['loggers'][logger]['level'] = DEBUG

            super().__init__(config)


class UvicornFormatter(DefaultFormatter, AccessFormatter):
    status_code_colours = {
        1: lambda code: click.style(str(code), fg='bright_white'),
        2: lambda code: click.style(str(code), fg='green'),
        3: lambda code: click.style(str(code), fg='blue'),
        4: lambda code: click.style(str(code), fg='yellow'),
        5: lambda code: click.style(str(code), fg='red'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level_name_colors[CRITICAL] = lambda level_name: click.style(str(level_name), fg='bright_red', bold=True)

    def formatMessage(self, record):
        if self.use_colors and hasattr(record, 'relativepath'):
            record.lineno = self.color_level_name(record.lineno, DEBUG)
            record.relativepath = self.color_level_name(record.relativepath, DEBUG)

        if record.name == 'uvicorn.access':
            _, _, _, _, status_code = record.args
            record.levelno = http_status_code_to_log_level(status_code)
            record.levelname = getLevelName(record.levelno)
            return AccessFormatter.formatMessage(self, record)
        elif record.name in ('uvicorn.error', 'fastapi'):
            if self.use_colors and record.levelname in (
                'WARNING',
                'ERROR',
                'CRITICAL',
            ):
                record.message = self.color_level_name(record.message.strip(), record.levelno)
            return DefaultFormatter.formatMessage(self, record)

        return ColourizedFormatter.formatMessage(self, record)


class JsonFormatter(_JsonFormatter):
    def format(self, record):
        if record.name == 'uvicorn.access':
            _, _, _, _, status_code = record.args
            record.levelno = http_status_code_to_log_level(status_code)
            record.levelname = getLevelName(record.levelno)

        return super().format(record)


class GunicornLogger(gunicorn.glogging.Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        DictConfigurator().configure()
        self.error_log = getLogger('gunicorn.error')
        self.access_log = getLogger('gunicorn.access')
