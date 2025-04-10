"""Django settings for billify project."""
import os
import sys
from pathlib import Path
import environ
import logging
import base64

# Configure logger
logger = logging.getLogger(__name__)

# Initialize environ
env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add the project root to the Python path
sys.path.append(str(BASE_DIR.parent))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ENVIRONMENT = env("ENVIRONMENT", default="development")

# Define allowed hosts from environment variables
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
    # Local apps
    # 'api' is not included here as it's not a Django app -> it actually could
    # be a Django app, but it's not a real app, it's just a collection of views
    # and endpoints.
    "infrastructure",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "billify.urls"

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

WSGI_APPLICATION = "billify.wsgi.application"

# Database
DATABASES = {
    "default": env.db(),
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": ("django.contrib.auth.password_validation." "UserAttributeSimilarityValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.parent / "static"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "config.settings.auth.BearerTokenAuthentication",
    ],
    # Authentication is not required during development, for now.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # Changed from IsAuthenticated
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.PageNumberPagination"),
    "PAGE_SIZE": 100,
}

# CORS settings
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# API Documentation
SPECTACULAR_SETTINGS = {
    "TITLE": "Billify API",
    "DESCRIPTION": "API for Billify cash flow management system",
    "VERSION": "1.0.0",
}

AUTH_USER_MODEL = "infrastructure.Account"

# Storage settings
if not DEBUG:
    # Production storage settings (S3/MinIO)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = env("DIGITAL_OCEAN_SPACES_KEY")
    AWS_SECRET_ACCESS_KEY = env("DIGITAL_OCEAN_SPACES_SECRET")
    AWS_STORAGE_BUCKET_NAME = env("DIGITAL_OCEAN_SPACES_NAME")
    AWS_S3_ENDPOINT_URL = "https://billify-staging.sfo3.digitaloceanspaces.com"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_VERIFY = True
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_LOCATION = "media"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",  # Set to DEBUG to capture all logs
            "class": "logging.StreamHandler",
            "formatter": "verbose",  # Use detailed logging format
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",  # Ensure root logger captures only INFO logs
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Show only INFO logs for Django
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",  # Prevent debug SQL queries from being logged
            "propagate": False,
        },
    },
}

LOG_LEVEL = env("LOG_LEVEL", default="INFO")

# Get log level from environment variable with a default of INFO
try:
    logger.setLevel(getattr(logging, LOG_LEVEL))
except AttributeError:
    logger.warning(f"Invalid log level '{LOG_LEVEL}', defaulting to INFO")
    logger.setLevel(logging.INFO)


# Ponto-Related Environment Variables
required_env_vars = [
    "PONTO_CLIENT_ID",
    "PONTO_CLIENT_SECRET",
    "PONTO_AUTH_URL",
    "PONTO_TOKEN_URL",
    "PONTO_REDIRECT_URI",
    "PONTO_PRIVATE_KEY_PASSWORD",
    "PONTO_SIGNATURE_KEY_ID",
    "FERNET_KEY",
]

# Check if any of the required environment variables are missing
missing_vars = [var for var in required_env_vars if not env(var)]

# If there are any missing variables, raise an error with the list of missing vars
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

PONTO_CLIENT_ID = env("PONTO_CLIENT_ID")
PONTO_CLIENT_SECRET = env("PONTO_CLIENT_SECRET")
PONTO_AUTH_URL = env("PONTO_AUTH_URL")
PONTO_TOKEN_URL = env("PONTO_TOKEN_URL")
PONTO_REDIRECT_URI = env("PONTO_REDIRECT_URI")
PONTO_CONNECT_BASE_URL = env("PONTO_CONNECT_BASE_URL")
PONTO_ACCOUNTS_ENDPOINT = "/accounts"
IBANITY_API_HOST = env("IBANITY_API_HOST")
PONTO_PRIVATE_KEY_PASSWORD = env("PONTO_PRIVATE_KEY_PASSWORD")
PONTO_SIGNATURE_KEY_ID = env("PONTO_SIGNATURE_KEY_ID")
PONTO_PAGE_LIMIT = 3
PONTO_PAGE_LIMIT_LIST = [1, 3, 5, 10, 15, 20, 25]

FERNET_KEY = env("FERNET_KEY")

# Validate and retrieve the FERNET_KEY
if FERNET_KEY is None:
    raise ValueError("FERNET_KEY not found in environment variables")

# Verify the FERNET_KEY format (should be a 44-character base64 encoded string)
if len(FERNET_KEY) != 44:
    raise ValueError("FERNET_KEY has invalid length. It should be a 44-character base64 encoded key.")

try:
    # Check if the key is base64 encoded
    base64.urlsafe_b64decode(FERNET_KEY)
    FERNET_KEY = FERNET_KEY.encode()
except Exception as e:
    logger.error(f"Invalid FERNET_KEY format: {e}")
    raise ValueError(f"FERNET_KEY is not in valid base64 format: {e}") from e

# Paths for certificates and keys
PONTO_CERTIFICATE_PATH = env("PONTO_CERTIFICATE_PATH")
PONTO_PRIVATE_KEY_PATH = env("PONTO_PRIVATE_KEY_PATH")

# List of valid ISO 4217 currency codes
VALID_ISO_CURRENCY_CODES = {
    "AED",
    "AFN",
    "ALL",
    "AMD",
    "ANG",
    "AOA",
    "ARS",
    "AUD",
    "AWG",
    "AZN",
    "BAM",
    "BBD",
    "BDT",
    "BGN",
    "BHD",
    "BIF",
    "BMD",
    "BND",
    "BRL",
    "BSD",
    "BTN",
    "BWP",
    "BYN",
    "BZD",
    "CAD",
    "CDF",
    "CHF",
    "CLP",
    "CNY",
    "COP",
    "CRC",
    "CUP",
    "CVE",
    "CZK",
    "DKK",
    "DOP",
    "DZD",
    "EGP",
    "ERN",
    "ETB",
    "EUR",
    "FJD",
    "FKP",
    "GBP",
    "GEL",
    "GGP",
    "GHS",
    "GIP",
    "GMD",
    "GNF",
    "GTQ",
    "GYD",
    "HKD",
    "HNL",
    "HRK",
    "HTG",
    "HUF",
    "IDR",
    "ILS",
    "IMP",
    "INR",
    "IQD",
    "IRR",
    "ISK",
    "JMD",
    "JOD",
    "JPY",
    "KES",
    "KGS",
    "KHR",
    "KPW",
    "KRW",
    "KWD",
    "KYD",
    "KZT",
    "LAK",
    "LBP",
    "LKR",
    "LRD",
    "LSL",
    "LYD",
    "MAD",
    "MDL",
    "MGA",
    "MKD",
    "MMK",
    "MNT",
    "MOP",
    "MRU",
    "MUR",
    "MVR",
    "MWK",
    "MXN",
    "MYR",
    "MZN",
    "NAD",
    "NGN",
    "NZD",
    "OMR",
    "PAB",
    "PEN",
    "PGK",
    "PHP",
    "PKR",
    "PLN",
    "PYG",
    "QAR",
    "RON",
    "RSD",
    "RUB",
    "RWF",
    "SAR",
    "SBD",
    "SCR",
    "SDG",
    "SEK",
    "SGD",
    "SHP",
    "SLL",
    "SOS",
    "SRD",
    "SSP",
    "THB",
    "TJS",
    "TMT",
    "TND",
    "TOP",
    "TRY",
    "TTD",
    "TWD",
    "TZS",
    "UAH",
    "UGX",
    "USD",
    "UYU",
    "UZS",
    "VES",
    "VND",
    "VUV",
    "WST",
    "XAF",
    "XAG",
    "XAU",
    "XCD",
    "XDR",
    "XOF",
    "XPF",
    "YER",
    "ZAR",
    "ZMW",
    "ZWL",
}

# Celery-Related Settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = None
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# CELERY BEAT SETTINGS
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
