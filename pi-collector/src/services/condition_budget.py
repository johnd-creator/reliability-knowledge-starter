"""Per-invocation GET-only budget for the collector-owned snapshot handoff."""
from urllib.parse import urlsplit

class ConditionGetBudget:
    def __init__(self, maximum):
        if type(maximum) is not int or not 1 <= maximum <= 25:
            raise ValueError("bounded snapshot request budget required")
        self.maximum, self.used = maximum, 0

    def install(self, client):
        original = client.request
        def request(method, path, *, params=None):
            parts = urlsplit(client.resolve_source_link(path)).path.rstrip('/').split('/')
            snapshot = (len(parts) >= 3 and parts[-3] == 'streams' and parts[-1] == 'value')
            resource = len(parts) >= 2 and parts[-2] in {'elements', 'assetdatabases', 'attributes'}
            direct = len(parts) >= 3 and parts[-3] == 'elements' and parts[-1] == 'attributes'
            if method.upper() != 'GET' or not (snapshot or resource or direct):
                raise ValueError("snapshot GET boundary rejected operation")
            if self.used >= self.maximum:
                raise ValueError("snapshot request budget exhausted")
            self.used += 1  # Includes failed attempts; never retries outside this counter.
            return original(method, path, params=params)
        client.request = request

SOURCE_ENV_NAMES = frozenset({'PI_WEB_API_BASE_URL','PI_USERNAME','PI_PASSWORD','PI_TOKEN',
    'PI_TIMEOUT_SECONDS','PI_RATE_LIMIT_SECONDS','PI_MAX_RESPONSE_BYTES','PI_VERIFY_TLS'})

def load_managed_source_environment(path):
    """Collector-only authority: read explicit private platform source keys.

    Never export DB/admin/other application settings from the shared file.
    Values are literal (same quote stripping as standalone dotenv); no expansion.
    """
    import os
    import stat
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size>65536:
            raise ValueError('private managed source authority required')
        values = {}
        for line in source:
            text = line.strip()
            if not text or text.startswith('#') or '=' not in text:
                continue
            name, value = text.split('=',1);name=name.strip()
            if name not in SOURCE_ENV_NAMES:
                continue
            if name in values:
                raise ValueError('ambiguous managed source configuration')
            value=value.strip()
            if value.startswith(('"',"'")):
                if len(value)<2 or value[-1]!=value[0]:
                    raise ValueError('invalid quoted source configuration')
                value=value[1:-1]
            if '\n' in value or '${' in value:
                raise ValueError('literal source configuration required')
            values[name]=value
    for name in SOURCE_ENV_NAMES:
        os.environ.pop(name,None)
    os.environ.update(values)
    os.environ['PI_CONFIG_MODE']='managed'
