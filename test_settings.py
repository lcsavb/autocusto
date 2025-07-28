"""
Test settings for AutoCusto
Uses SQLite for testing instead of PostgreSQL
"""

from autocusto.settings import *

# Override database settings for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Enable migrations for frontend tests that need real database structure
# Note: Unit tests can still use --nomigrations flag if needed for speed

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable debug for tests  
DEBUG = False

# Disable SSL-related settings for tests (allow HTTP)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Use simple cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Test-specific configuration flag
# This will be used by models to handle test-specific behavior
TEST_ENVIRONMENT = True

# Disable most logging during tests to reduce noise
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'CRITICAL',
    },
    # Silence analytics logging during tests
    'loggers': {
        'analytics': {
            'handlers': ['null'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'analytics.signals': {
            'handlers': ['null'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
}

# Disable analytics signals completely during tests
ANALYTICS_ENABLED = False
