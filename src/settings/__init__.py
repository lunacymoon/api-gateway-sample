import os

APP_TITLE = os.getenv('APP') or 'ECIP API Gateway'
API_VERSION = os.getenv('API_VERSION') or '?'
APP_URL_VERSION = (1, 0)
API_DOCS: bool = True if os.getenv('API_DOCS', '').lower() == 'true' else False
ENV = os.getenv('ENV', 'local')
DEBUG = os.getenv('DEBUG', '')
TEST = os.getenv('TEST', '')
LOGGING_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'logging_conf.yaml')
ORIGIN_REGEX = os.getenv('ORIGINS', '').strip() or '.*'

IS_LOCAL_ENV: bool = ENV == 'local'
IS_DEBUG: bool = True if DEBUG else False
IS_TEST: bool = True if TEST else False

TIMEOUT_SECONDS: int = int(os.getenv('TIMEOUT_SECOND') or '60')
