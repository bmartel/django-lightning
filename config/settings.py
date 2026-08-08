"""
Django settings for django-lightning project using django-bolt.
"""

from pathlib import Path

import dj_database_url

from app.config import EnvSettings

BASE_DIR = Path(__file__).resolve().parent.parent

# Load type-safe environment configuration powered by msgspec.Struct
env = EnvSettings.load_from_env(base_dir=BASE_DIR)

SECRET_KEY = env.SECRET_KEY
DEBUG = env.DEBUG
ENABLE_MCP_SERVER = env.ENABLE_MCP_SERVER
ALLOWED_HOSTS = env.ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = env.CSRF_TRUSTED_ORIGINS

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_bolt",
    "app.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Custom User Model out of the box
AUTH_USER_MODEL = "app.User"

# Database configuration.
# Under the async ORM each query runs in a sync_to_async worker thread, so persistent
# per-thread connections (CONN_MAX_AGE > 0) accumulate and can exhaust the server's
# max_connections. Instead use a real connection pool (psycopg3) with CONN_MAX_AGE=0.
DATABASE_URL = env.DATABASE_URL
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=0,
        conn_health_checks=True,
    )
}

if DATABASES["default"].get("ENGINE") == "django.db.backends.postgresql":
    # Bounded psycopg3 pool shared across worker threads. Tune min/max to your DB's
    # max_connections and process/worker count. If you front the DB with PgBouncer in
    # transaction mode, drop this pool and keep CONN_MAX_AGE=0.
    _db_options = DATABASES["default"].setdefault("OPTIONS", {})
    _db_options["pool"] = {"min_size": 2, "max_size": 10, "timeout": 10}

# Cache & Redis configuration
REDIS_URL = env.REDIS_URL
USE_REDIS_CACHE = bool(env.USE_REDIS_CACHE and env.REDIS_URL)

if USE_REDIS_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "django-lightning-cache",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS setup
# Only reflect all origins in local development; production must use an explicit allowlist.
CORS_ALLOW_ALL_ORIGINS = DEBUG and not env.CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = env.CORS_ALLOWED_ORIGINS

# Security hardening. These are enforced whenever DEBUG is off (i.e. in production).
# Django's own `manage.py check --deploy` verifies this block.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    # Correctly detect HTTPS behind a TLS-terminating proxy / load balancer (Caddy/Fly/k8s).
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.SECURE_SSL_REDIRECT
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    # HTTP Strict Transport Security. Start conservative; raise max-age once verified.
    SECURE_HSTS_SECONDS = env.SECURE_HSTS_SECONDS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Request body / form field limits to bound memory use and multipart abuse.
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple" if DEBUG else "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if not DEBUG else "DEBUG",
    },
}
