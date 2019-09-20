import logging.config
import os
import re

import environ

env = environ.Env()

# ---------
# General setup
# ---------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = env.bool("DEBUG", False)
SECRET_KEY = env.str("SECRET_KEY", "you-should-set-this-probably")
SITE_ID = 1

# ---------
# Basic Django settings
# ---------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = env.str("STATIC_ROOT", os.path.join(BASE_DIR, "static"))

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

ROOT_URLCONF = "wallet.urls"
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
            ]
        },
    }
]
WSGI_APPLICATION = "wallet.wsgi.application"


# ---------
# Accounts and users
# ---------

AUTH_USER_MODEL = "core.WalletUser"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
LOGIN_REDIRECT_URL = "/"


# ----------
# Django applications
# ----------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
LIBRARY_APPS = ["bootstrap4", "allauth", "allauth.account", "allauth.socialaccount"]
PROJECT_APPS = ["core"]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + LIBRARY_APPS

if DEBUG:
    INSTALLED_APPS += ["django.contrib.admin"]


# ---------
# Upvest client settings
# ---------

UPVEST_OAUTH_CLIENT_ID = env.str("UPVEST_OAUTH_CLIENT_ID")
UPVEST_OAUTH_CLIENT_SECRET = env.str("UPVEST_OAUTH_CLIENT_SECRET")
UPVEST_API_KEY_ID = env.str("UPVEST_API_KEY_ID")
UPVEST_API_KEY_SECRET = env.str("UPVEST_API_KEY_SECRET")
UPVEST_API_KEY_PASSPHRASE = env.str("UPVEST_API_KEY_PASSPHRASE")
UPVEST_BACKEND = env.str("UPVEST_BACKEND", "https://api.playground.upvest.co/")
UPVEST_USER_AGENT = env.str("UPVEST_USER_AGENT", "upvest-wallet/default")

# ---------
# Hosting information
# ---------
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
csrf_header = "X-csrf-wallet"
CSRF_COOKIE_NAME = "wallet_csrf"
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN", default="localhost")
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", False)
CSRF_HEADER_NAME = "HTTP_%s" % re.sub("-", "_", csrf_header.upper())
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["localhost"])

SESSION_COOKIE_NAME = "wallet_session"
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", default="localhost")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", False)


# ---------
# Databases
# ---------
if "DATABASE_URL" in os.environ:
    DATABASES = {"default": env.db()}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "sqlite3.db"),
            "USER": "",
            "PASSWORD": "",
            "HOST": "",
            "PORT": "",
        }
    }


# ----------
# Email
# ----------
if "EMAIL_URL" in env:
    EMAIL_CONFIG = env.email_url("EMAIL_URL", default=None)
    vars().update(EMAIL_CONFIG)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ----------
# Logging
# ----------

LOGGING_CONFIG = None

logging.config.dictConfig({"version": 1, "disable_existing_loggers": True})

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "moreinfo": {
            "format": "%(asctime)s : %(module)-10s-%(funcName)-10s-%(lineno)-3s : %(levelname)7s] : %(message)s",
            "style": "%",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "default": {"format": "{levelname} {message}", "style": "{", "datefmt": "%Y-%m-%d %H:%M:%S"},
    },
    "handlers": {
        "null": {"class": "logging.NullHandler"},
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
        "verboseconsole": {"class": "logging.StreamHandler", "formatter": "moreinfo"},
    },
}

if DEBUG:
    LOGGING["loggers"] = {
        "": {"handlers": ["verboseconsole"], "level": "INFO", "propagate": True},
        "wallet": {"handlers": ["verboseconsole"], "level": "DEBUG", "propagate": False},
    }
else:
    handlers = ["console"]
    LOGGING["loggers"] = {
        "": {"handlers": handlers, "level": "WARN", "propagate": True},
        "wallet": {"handlers": handlers, "level": "INFO", "propagate": True},
    }

logging.config.dictConfig(LOGGING)


# ------------
# Reporting
# ------------

USE_STATSD = env.bool("USE_STATSD", False)
if USE_STATSD:
    STATSD_PATCHES = ["django_statsd.patches.db", "django_statsd.patches.cache"]
    STATSD_HOST = env.str("STATSD_HOST", "localhost")
    STATSD_PORT = env.int("STATSD_PORT", 5602)
    MIDDLEWARE = [
        "django_statsd.middleware.GraphiteRequestTimingMiddleware",
        "django_statsd.middleware.GraphiteMiddleware",
    ] + MIDDLEWARE
