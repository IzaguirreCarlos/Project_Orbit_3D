"""
ProjectForge 3D — Production Settings
Render.com deployment: SSL termination at load balancer, $PORT injection.
"""
from .base import *  # noqa
import os

DEBUG = False

# ─── Hosts ────────────────────────────────────────────────────────
# En Render el hostname cambia por deploy. Permite override via env var.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# ─── Proxy SSL (Render termina SSL antes de llegar al contenedor) ──
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ─── Security ─────────────────────────────────────────────────────
# SECURE_SSL_REDIRECT desactivado: Render ya fuerza HTTPS en su CDN.
# Si está activo con el proxy, puede causar redirect loops → 504.
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=[
        'https://projectforge-web.onrender.com',
        'https://*.onrender.com',
    ]
)

# ─── CORS ─────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['https://projectforge-web.onrender.com']
)
CORS_ALLOW_ALL_ORIGINS = False

# ─── Cache & Channels ─────────────────────────────────────────────
# Usa Redis solo si REDIS_URL apunta a un host externo real.
# URLs locales/Docker → in-memory (sin conexión de red que pueda colgar).
def _is_external_redis(url: str) -> bool:
    """Devuelve True solo si la URL apunta a un Redis externo real."""
    if not url:
        return False
    _local = ('localhost', '127.0.0.1', '0.0.0.0', '::1')
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname or ''
        return host not in _local and host != 'redis'
    except Exception:
        return False


_redis_url = os.environ.get('REDIS_URL', '')

if _is_external_redis(_redis_url):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': _redis_url,
        }
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {'hosts': [_redis_url]},
        }
    }
else:
    # Sin Redis externo → in-memory (funcional para instancia única en Render)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'projectforge-prod',
        }
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

# ─── Celery ───────────────────────────────────────────────────────
# Sin broker externo → modo eager para evitar intentos de conexión Redis
_broker_url = os.environ.get('CELERY_BROKER_URL', '')

if not _is_external_redis(_broker_url):
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = False

# ─── Logging estructurado ─────────────────────────────────────────
# Formatter JSON con fallback a texto plano si pythonjsonlogger falla
try:
    import pythonjsonlogger.jsonlogger  # noqa
    _log_formatter: dict = {
        '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
    }
except ImportError:
    _log_formatter = {'format': '[%(levelname)s] %(asctime)s %(name)s: %(message)s'}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'production': _log_formatter,
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'production',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
