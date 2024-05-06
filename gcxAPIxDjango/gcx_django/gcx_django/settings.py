import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'g_8e%$ig0%)sikt_#jk88mj^&5@p=rn*vrrm*r8s8-4=bzz8e6')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = os.environ.get('DJANGO_DEBUG', True)

CONFIGURATION_MODE = os.getenv('CONFIGURATION_MODE', 'developement')

ALLOWED_HOSTS = ['127.0.0.1', '3.208.115.125']

CSRF_TRUSTED_ORIGINS = ['127.0.0.1', '3.208.115.125']

AUTH_USER_MODEL = 'gcxAPIx.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Below are the custom apps
    'rest_framework',
    'rest_framework.authtoken',
    'gcxAPIx',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gcx_django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gcx_django.wsgi.application'

DATABASES = {
    # 'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / 'db.sqlite3',
    # },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gcx_testing',
        'USER': 'postgres',
        'PASSWORD': '7896005',
        'HOST': 'localhost',
        'PORT': '5432',
        # 'OPTIONS': {
        #    'service': 'my_service',
        #    'passfile': '.my_pgpass',
        # },
    }
}


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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATIC_URL = '/static/'

APPEND_SLASH = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

MEDIA_URL = '/uploads/'
MEDIA_ROOT = '/var/www/GCX/upload/'
#REST_FRAMEWORK = {
#   'TEST_REQUEST_DEFAULT_FORMAT': 'json',
#   'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
#   'DEFAULT_RENDERER_CLASSES': (
#       'rest_framework.renderers.JSONRenderer',
#   ),
#

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.

    # 'DEFAULT_RENDERER_CLASSES': [
    #    'rest_framework.renderers.JSONRenderer',
    #    'rest_framework.renderers.BrowsableAPIRenderer',
    # ],
    # 'DEFAULT_PARSER_CLASSES': [
    #    'rest_framework.parsers.JSONParser',
    #    'rest_framework.parsers.FormParser',
    #    'rest_framework.parsers.MultiPartParser',
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'gcxAPIx.auth.LoginAuth'
        #'rest_framework.authentication.SessionAuthentication',
        #'rest_framework.authentication.BasicAuthentication',
        #'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        #'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    # 'DEFAULT_SCHEMA_CLASS': [
    #    'rest_framework.schemas.openapi.AutoSchema',
    # ]
}
# Add different environment variables for different modes
if CONFIGURATION_MODE == 'developement':
    os.environ['API_ACCESS_KEY'] = 'Bearer 2685bb3a2ffc6eabccc3b6ebbfee886cd2d7061e'
    os.environ['STRIPE_SECRET_KEY'] = 'sk_test_51L2VAGCGbZSVDA9YVsEnkRRUtBQn1UcmlTO0xuSp8DWczg7Gch5ERYuBtgiNdtI6fdoGa30ZLBD6X55aZYJWfyxG00e9Hk9xTL'
    #os.environ['STRIPE_ENDPOINT_SECRET'] = 'whsec_sAXeE3Q36l25sf578pnjOi4Uyt8Bvs1m'
    os.environ['STRIPE_ENDPOINT_SECRET'] = 'whsec_7d01894cf5554472f485aa1c6d00af725e4c6e2a8cde9a38932259de6e5306d7'
    os.environ['STRIPE_PUBLISH_KEY'] = 'pk_test_51L2VAGCGbZSVDA9YlxCbxygJX29SWWxoTFK3Utqqg2Ea5qQS2BguxotP2gXkLEErosaqyw61cBCav578Q7cDD5kW00ZV5FX2IZ'
elif CONFIGURATION_MODE == 'production':
    os.environ['STRIPE_SECRET_KEY'] = 'sk_test_51L2VAGCGbZSVDA9YVsEnkRRUtBQn1UcmlTO0xuSp8DWczg7Gch5ERYuBtgiNdtI6fdoGa30ZLBD6X55aZYJWfyxG00e9Hk9xTL'
    #os.environ['STRIPE_ENDPOINT_SECRET'] = 'whsec_sAXeE3Q36l25sf578pnjOi4Uyt8Bvs1m'
    os.environ['STRIPE_ENDPOINT_SECRET'] = 'whsec_7d01894cf5554472f485aa1c6d00af725e4c6e2a8cde9a38932259de6e5306d7'
    os.environ['STRIPE_PUBLISH_KEY'] = 'pk_test_51L2VAGCGbZSVDA9YlxCbxygJX29SWWxoTFK3Utqqg2Ea5qQS2BguxotP2gXkLEErosaqyw61cBCav578Q7cDD5kW00ZV5FX2IZ'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    '127.0.0.1:8000',
    '3.208.115.125'
]

CELERY_TIMEZONE = "America/New_York"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = 'amqp://guest:guest@localhost'
