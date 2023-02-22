
from os import environ

LOG_LEVEL = environ.get('LOG_LEVEL', 'WARNING')
DEFAULT_URL = "fabric.dev.aws.ydata.ai"
BACKOFF = 10  # 10s backoff between requests
