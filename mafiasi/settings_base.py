import os

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join('/', 'app', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join('/', 'app', 'static', 'django')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/django/'

# Additional locations of static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ]},
    },
]

ROOT_URLCONF = 'mafiasi.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'mafiasi.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'oauth2_provider',
    'corsheaders',
    'mafiasi.base',
    'mafiasi.dashboard',
)
INSTALLED_APPS_LATE = (
    'django.contrib.admin',
    'django.contrib.admindocs',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

AUTH_USER_MODEL = 'base.Mafiasi'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/dashboard/'


from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG: 'alert-info',
    message_constants.INFO: 'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger'
}

LOCALE_PATHS = (os.path.join(ROOT_DIR, 'locale'),)

LANGUAGES = (
    ('de', 'Deutsch'),
    ('en', 'English'),
    ('fr', 'Français'),
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        #        'mail_admins': {
        #            'level': 'ERROR',
        #            'filters': ['require_debug_false'],
        #            'class': 'django.utils.log.AdminEmailHandler'
        #        }
    },
    'loggers': {
        'django.request': {
            'handlers': [],  # 'mail_admins'
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

MATHJAX_ROOT = '/usr/share/javascript/mathjax/'

BANNER_IMG = ""

TEMPLATE_ALLOWABLE_SETTINGS_VALUES = (
    "REGISTER_ENABLED",
    "MAIL_SIGNATURE",
    "PROJECT_NAME",
    "PROJECT_BANNER",
    "MAIL_GREETING",
    "MAIL_INCLUDE_GERMAN",
    "MAIL_GREETING_DE",
    "MAIL_GREETING_EN",
    "BANNER_IMG",
    "GUEST_INVITE_HINT",
    "USER_LOGIN_HINT",
    "GUEST_INVITE_INSTRUCTION_LINK",
    "RAVEN_PUBLIC_DSN",
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'mafiasi.base.validation.AsciiValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
