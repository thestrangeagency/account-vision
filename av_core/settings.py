import sys

import dj_database_url
import os
import raven
from django.urls import reverse_lazy
from dotenv import load_dotenv, find_dotenv
from os.path import join

# Optionally store env vars in a .env file
load_dotenv(find_dotenv(), verbose=True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "ugpC8Q;xvz&gTh5l'SE^aZucuUP13rc|uVO&%f)k4As00dLy2!MIQbBm5|TG2TRK")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", False)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# force SSL on production site
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    ALLOWED_HOSTS = ['acvi-stage.herokuapp.com', 'acvi.herokuapp.com', 'account.vision', 'www.account.vision']
else:
    ALLOWED_HOSTS = ['*']

TESTING = sys.argv[1:2] == ['test']
MAIL_OFF = False

AUTH_USER_MODEL = 'av_account.AvUser'

LOGIN_REDIRECT_URL = reverse_lazy('login_redirect')
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = reverse_lazy('login')
VERIFY_URL = reverse_lazy('trust')

DEFAULT_FROM_EMAIL = 'Account Vision <no-reply@account.vision>'
SERVER_EMAIL = 'info@accoun.vision'

ADMINS = [('Lucas', 'lucas@strange.agency')]
DEFAULT_CONTACT = os.environ.get("DEFAULT_CONTACT", 'lucas@strange.agency')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # for flatpages
    'django.contrib.sites',
    'django.contrib.flatpages',

    # for customizing forms and using TemplatesSetting renderer
    'django.forms',

    # thirdparty
    'debug_toolbar',
    'phonenumber_field',
    'django_bootstrap_breadcrumbs',
    'crispy_forms',
    'django_extensions',
    'menu_generator',
    'rest_framework',
    'django_messages',
    'twilio',
    'django_agent_trust',
    'actstream',

    # account vision
    'av_core',
    'av_account',
    'av_profile',
    'av_contact',
    'av_emails',
    'av_clients',
    'av_returns',
    'av_uploads',
    'av_messages',
    'av_team',
    'av_payment',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',

    # thirdparty
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'ip_restriction.IpWhitelister',
    'django_agent_trust.middleware.AgentMiddleware',
]

ROOT_URLCONF = 'av_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [join(PROJECT_ROOT + '/templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'av_core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Change 'default' database configuration with $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

if os.environ.get('CI'):
    DATABASES['default']['TEST'] = db_from_env
    TEST_RUNNER = 'av_utils.heroku_test_runner.HerokuDiscoverRunner'

if DEBUG:
    AUTH_PASSWORD_VALIDATORS = []
    INTERNAL_IPS = ('127.0.0.1')
    DEFAULT_HTTP_PROTOCOL = 'http'
else:
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]
    DEFAULT_HTTP_PROTOCOL = 'https'

LOG_LEVEL = 'INFO' if DEBUG and not TESTING else 'WARN'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] '
                       'pathname=%(pathname)s lineno=%(lineno)s '
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'av_logger': {
            'handlers': ['console', ],
            'level': LOG_LEVEL,
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = False
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# django-ip-restriction, give access to the admin login, and let authenticated users view the site
# RESTRICT_IPS = True # setting this in host env
ALLOW_ADMIN = True
ALLOW_AUTHENTICATED = True

# django_bootstrap_breadcrumbs
BREADCRUMBS_TEMPLATE = 'django_bootstrap_breadcrumbs/bootstrap4.html'

# django-crispy-forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# django-menu-generator
from .menus import *

# rest_framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
}

# s3
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', 'test-key')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'test-secret')
AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME', 'test-bucket')
AWS_REGION = os.environ.get('AWS_REGION', 'us-test-1')

AWS_DESTINATIONS = {
    'uploads': {
        'auth': lambda u: u.is_authenticated(),
        'content_length_range': (1, 10000000),
        'acl': 'private',
        'cache_control': 'max-age=2592000',  # 60x60x24x30
        'server_side_encryption': 'AES256',
        'key': 'uploads',
    },
}

# ses
EMAIL_BACKEND = 'av_core.backends.boto.EmailBackend'
AWS_SES_REGION = os.environ.get('AWS_SES_REGION', 'us-east-1')

# phonenumber_field
PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'US'

# twilio
# @override_settings doesn't seem to work so overriding vars for testing here
if TESTING:
    TWILIO_ACCOUNT_SID = 'AC9d398c13e8e779d8d6acb7d28d4fb8fa'
    TWILIO_AUTH_TOKEN = '08312ca964c88e1974b33067166db073'
    TWILIO_FROM_NUMBER = '+15005550006'
else:
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')

# django_agent_trust
AGENT_TRUST_DAYS = None
AGENT_INACTIVITY_DAYS = 30

# django_messages
DJANGO_MESSAGES_NOTIFY = False  # disable built-in emails

# stripe
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

STRIPE_PLANS = {
    'yearly': {
        'a': os.environ.get("STRIPE_PLAN_A_Y", "plan_ay"),
        'b': os.environ.get("STRIPE_PLAN_B_Y", "plan_by"),
        'c': os.environ.get("STRIPE_PLAN_C_Y", "plan_cy"),
    },
    'monthly': {
        'a': os.environ.get("STRIPE_PLAN_A_M", "plan_am"),
        'b': os.environ.get("STRIPE_PLAN_B_M", "plan_bm"),
        'c': os.environ.get("STRIPE_PLAN_C_M", "plan_cm"),
    }
}

STRIPE_DEFAULT_PLAN = STRIPE_PLANS['monthly']['c']

# notifications
NOTIFICATION_NUMBERS = (
    '+13106663912',
)

SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': raven.fetch_git_sha(os.path.abspath(os.pardir)),
    }
    INSTALLED_APPS = INSTALLED_APPS + [
        'raven.contrib.django.raven_compat',
    ]
