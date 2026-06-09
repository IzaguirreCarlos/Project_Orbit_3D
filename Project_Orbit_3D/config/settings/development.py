"""
ProjectForge 3D — Development Settings
"""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

# ─── Debug Toolbar ───────────────────────────────────────────
INSTALLED_APPS += ['debug_toolbar']  # noqa
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
INTERNAL_IPS = ['127.0.0.1', '0.0.0.0']

# ─── Dev: usar SQLite si no hay .env ─────────────────────────
# DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

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
