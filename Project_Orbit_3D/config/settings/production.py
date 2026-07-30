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

# ─── Cache ────────────────────────────────────────────────────────
# Usa Redis si REDIS_URL está definida con una URL real (no Docker).
# Sin Redis configurado en Render → usa cache en memoria (sin timeout).
_redis_url = os.environ.get('REDIS_URL', '')
_redis_is_docker = _redis_url.startswith('redis://redis:')

if _redis_url and not _redis_is_docker:
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
    # Sin Redis → in-memory (funcional para instancia única en Render)
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
# Sin broker Redis real → modo eager para no colgar en .delay()
_broker_url = os.environ.get('CELERY_BROKER_URL', '')
_broker_is_docker = _broker_url.startswith('redis://redis:')

if not _broker_url or _broker_is_docker:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = False

# ─── Logging estructurado ─────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
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
