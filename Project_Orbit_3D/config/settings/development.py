"""
Project_Orbit_3D — Development Settings
"""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

# ─── Debug Toolbar ───────────────────────────────────────────
INSTALLED_APPS += ['debug_toolbar']  # noqa
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
INTERNAL_IPS = ['127.0.0.1', '0.0.0.0']

# ─── Dev: SQLite con timeout para evitar "database is locked" ─
DATABASES['default'].setdefault('OPTIONS', {})  # noqa
DATABASES['default']['OPTIONS']['timeout'] = 20  # noqa

# ─── CORS abierto en dev ──────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ─── Caché en memoria (sin Redis) ────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'projectforge-dev',
    }
}

# ─── Channels en memoria (sin Redis) ─────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# ─── Throttling desactivado en dev ───────────────────────────
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []  # noqa

# ─── Celery en modo eager (sin broker) en dev ─────────────────
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = False

# ─── Logging ─────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'apps': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
