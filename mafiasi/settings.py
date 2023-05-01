import os.path
import subprocess
from pathlib import Path

from environs import Env

env = Env()
env.read_env(env.path("MAFIASI_ENV_FILE", default=".env"))

BASE_DIR = Path(__file__).parent.parent

DEBUG = env.bool("MAFIASI_DEBUG", default=False)
TESTING = env.bool("MAFIASI_TESTING", default=False)

# Feature toggles
ENABLE_JABBER_INTEGRATION = env.bool("MAFIASI_ENABLE_JABBER_INTEGRATION")
ENABLE_EP_INTEGRATION = env.bool("MAFIASI_ENABLE_EP_INTEGRATION")
ENABLE_VAULT_INTEGRATION = env.bool("MAFIASI_ENABLE_VAULT_INTEGRATION")

DATABASES = {
    "default": env.dj_db_url("MAFIASI_DB"),
}

OPENID_ISSUER = env.str("MAFIASI_OPENID_ISSUER", default="https://identity.mafiasi.de/realms/mafiasi")
OPENID_CLIENT_ID = env.str("MAFIASI_OPENID_CLIENT_ID", default="mafiasi-dashboard")
OPENID_CLIENT_SECRET = env.str("MAFIASI_OPENID_CLIENT_SECRET", required=True)
OPENID_SCOPE = "openid profile email groups"
OPENID_CREATE_USER_FUNC = "mafiasi.registration.user_mapping.create_user_from_token"
OPENID_UPDATE_USER_FUNC = "mafiasi.registration.user_mapping.update_user_from_token"

KEYCLOAK_ACCOUNT_CONSOLE_URL = env.str(
    "MAFIASI_KEYCLOAK_ACCOUNT_CONSOLE_URL", default="https://identity.mafiasi.de/realms/mafiasi/account"
)

OPENID_SYNC_SUPERUSER = env.bool("MAFIASI_OPENID_SYNC_SUPERUSER", default=True)
if OPENID_SYNC_SUPERUSER:
    OPENID_SUPERUSER_GROUP = env.str("MAFIASI_OPENID_SUPERUSER_GROUP", default="Server-AG")

LDAP_SERVERS = {}
ENABLE_LDAP_AUTH_BACKEND = env.bool("MAFIASI_ENABLE_LDAP_AUTH_BACKEND", default=True)
if ENABLE_LDAP_AUTH_BACKEND:
    LDAP_SERVERS["default"] = {
        "URI": env.str("MAFIASI_LDAP_URI"),
        "BIND_DN": env.str("MAFIASI_LDAP_BIND_DN"),
        "BIND_PASSWORD": env.str("MAFIASI_LDAP_BIND_PW"),
    }
    import ldap
    from django_auth_ldap.config import LDAPSearch

    AUTHENTICATION_BACKENDS = (
        "django_auth_ldap.backend.LDAPBackend",
        "django.contrib.auth.backends.ModelBackend",
    )
    AUTH_LDAP_BIND_DN = ""
    AUTH_LDAP_BIND_PASSWORD = ""
    AUTH_LDAP_USER_SEARCH = LDAPSearch(env.str("MAFIASI_LDAP_USER_SEARCH_DN"), ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
    AUTH_LDAP_ALWAYS_UPDATE_USER = False

    ROOT_DN = env.str("MAFIASI_LDAP_ROOT_DN")

ENABLE_LDAP_REGISTRATION = env.bool("MAFIASI_ENABLE_LDAP_REGISTRATION")
if ENABLE_LDAP_REGISTRATION:
    LDAP_SERVERS["registration"] = {
        "CA": env.str("MAFIASI_LDAP_REGISTRATION_CA"),
        "URI": env.str("MAFIASI_LDAP_REGISTRATION_URI"),
        "BIND_DN": env.str("MAFIASI_LDAP_REGISTRATION_BIND_DN"),
        "BIND_PASSWORD": env.str("MAFIASI_LDAP_REGISTRATION_BIND_PW"),
    }
    REGISTRATION_LDAP_USER_SEARCH_FAST = LDAPSearch(
        "ou=Users,ou=studenten,dc=informatik,dc=uni-hamburg,dc=de",
        ldap.SCOPE_SUBTREE,
        "(uid=%(uid)s)",
        ["mail", "gecos", "gidNumber"],
    )
    REGISTRATION_LDAP_USER_SEARCH_SLOW = LDAPSearch(
        "dc=informatik,dc=uni-hamburg,dc=de", ldap.SCOPE_SUBTREE, "(uid=%(uid)s)", ["mail", "gecos", "gidNumber"]
    )
    REGISTRATION_LDAP_GROUP_SEARCH = LDAPSearch(
        "dc=informatik,dc=uni-hamburg,dc=de",
        ldap.SCOPE_SUBTREE,
        "(&(gidNumber=%(gidNumber)s)(objectClass=group))",
        ["name"],
    )

REGISTER_ENABLED = True
PRIMARY_DOMAIN = "informatik.uni-hamburg.de"
REGISTER_DOMAINS = ["informatik.uni-hamburg.de", "physnet.uni-hamburg.de", "hiforum.de"]
REGISTER_DOMAIN_MAPPING = {
    "physnet.uni-hamburg.de": "physnet",
    "hiforum.de": "hiforum",
}
ACCOUNT_PATTERNS = {
    "informatik.uni-hamburg.de": r"\d?[a-z]+",
    "physnet.uni-hamburg.de": r"[a-z]+",
}

ALLOWED_HOSTS = env.list("MAFIASI_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "::1"])

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Europe/Berlin"
LANGUAGE_CODE = "en-us"

SECRET_KEY = env.str("MAFIASI_SECRET_KEY")

MEDIA_ROOT = str(env.path("MAFIASI_MEDIA_ROOT", default=BASE_DIR / "media"))
MEDIA_URL = "/media/"

STATIC_ROOT = str(env.path("MAFIASI_STATIC_ROOT", default=BASE_DIR / "staticfiles"))
STATIC_URL = "/static/django/"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "mafiasi.base.middleware.InvalidMailMiddleware",
]

INSTALLED_APPS = [
    i
    for i in [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.humanize",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
        "widget_tweaks",
        "oauth2_provider",
        "corsheaders",
        "simple_openid_connect.integrations.django",
        ### internal
        "mafiasi.base",
        "mafiasi.dashboard",
        "mafiasi.groups",
        "mafiasi.guests",
        "mafiasi.registration",
        "mafiasi.mail",
        "mafiasi.mailinglist",
        "mafiasi.teaching",
        ### dashboard apps
        "mafiasi.wiki",
        "mafiasi.gprot",
        "mafiasi.nextcloud",
        "mafiasi.etherpad",
        "mafiasi.bitpoll",
        "mafiasi.matrix",
        "mafiasi.git",
        "mafiasi.sogo",
        "mafiasi.tauschen",
        "mafiasi.link_shortener",
        "mafiasi.vault" if ENABLE_VAULT_INTEGRATION else None,
        "mafiasi.pks",
        "mafiasi.kanboard",
        "mafiasi.whiteboard",
        "mafiasi.mattermost",
        "mafiasi.discourse",
        "mafiasi.fb18",
        ###
        "django.contrib.admin",
        "django.contrib.admindocs",
    ]
    if i is not None
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.media",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
            "debug": DEBUG,
        },
    },
]

TEMPLATE_ALLOWABLE_SETTINGS_VALUES = [
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
    "VAULT_URL",
    "KEYCLOAK_ACCOUNT_CONSOLE_URL",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ROOT_URLCONF = "mafiasi.urls"

WSGI_APPLICATION = "mafiasi.wsgi.application"

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

TEST_RUNNER = "django.test.runner.DiscoverRunner"

AUTH_USER_MODEL = "base.Mafiasi"

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/dashboard/"
USER_LOGIN_HINT = "Note: For our account names we use two digits for year (e.g. <strong>13doe</strong> instead of 3doe)"

from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG: "alert-info",
    message_constants.INFO: "alert-info",
    message_constants.SUCCESS: "alert-success",
    message_constants.WARNING: "alert-warning",
    message_constants.ERROR: "alert-danger",
}

LOCALE_PATHS = [str(BASE_DIR / "locale")]

LANGUAGES = (
    ("de", "Deutsch"),
    ("en", "English"),
    ("fr", "Français"),
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": None,
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CORS_ORIGIN_ALLOW_ALL = True

MATHJAX_ROOT = "/usr/share/javascript/mathjax/"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "mafiasi.base.validation.AsciiValidator",
    },
]

if ENABLE_JABBER_INTEGRATION:
    JABBER_DOMAIN = "jabber.mafiasi.de"
    JABBER_CERT_FINGERPRINT_FILE = str(env.path("MAFIASI_JABBER_CERT_FINGERPRINT_FILE"))
    if os.path.isfile(JABBER_CERT_FINGERPRINT_FILE):
        JABBER_CERT_FINGERPRINT = (
            subprocess.check_output(["openssl", "x509", "-in", JABBER_CERT_FINGERPRINT_FILE, "-noout", "-fingerprint"])
            .decode()
            .strip()
        )
    else:
        JABBER_CERT_FINGERPRINT = ""
    INSTALLED_APPS.insert(INSTALLED_APPS.index("mafiasi.mattermost"), "mafiasi.jabber")
    DATABASES["jabber"] = env.dj_db_url("MAFIASI_DB_JABBER", default="sqlite://:memory:")

if ENABLE_EP_INTEGRATION:
    DATABASES["etherpad"] = env.dj_db_url("MAFIASI_DB_ETHERPAD", default="sqlite://:memory:")
    ETHERPAD_API_KEY = env.str("MAFIASI_EP_API_KEY")
    ETHERPAD_URL = "https://ep.mafiasi.de"
    EP_COOKIE_DOMAIN = ".mafiasi.de"

if ENABLE_VAULT_INTEGRATION:
    VAULT_URL = env.str("MAFIASI_VAULT_URL", default="https://vault.mafiasi.de")
    VAULT_ADMIN_TOKEN = env.str("MAFIASI_VAULT_ADMIN_TOKEN")

DATABASE_ROUTERS = ["mafiasi.jabber.dbrouter.JabberRouter", "ldapdb.router.Router"]

PROJECT_NAME = "mafiasi.de"
PROJECT_BANNER = "Mafiasi Hub"
BANNER_IMG = ""

HKP_URL = "hkps://mafiasi.de"

# Maximum sizes for gprot images / pdfs in MB
GPROT_IMAGE_MAX_SIZE = 1
GPROT_PDF_MAX_SIZE = 5

IMPRINT_URL = "https://wiki.mafiasi.de/Fachschaft_Informatik:Impressum"
WIKI_URL = "https://www2.informatik.uni-hamburg.de/Fachschaft/wiki/"
SOGO_URL = "https://sogo.mafiasi.de"
GIT_URL = "https://git.mafiasi.de"
TAUSCHEN_URL = "https://tauschen.mafiasi.de"
MATTERMOST_URL = "https://mattermost.mafiasi.de"
NEXTCLOUD_URL = "https://cloud.mafiasi.de"
JITSI_URL = "https://conference.mafiasi.de"
DISCOURSE_URL = "https://archiv.mafiasi.de/forum/discourse"
FB18_URL = "https://archiv.mafiasi.de/forum/fb18"
WIKI_URL = "https://wiki.mafiasi.de"
BITPOLL_URL = "https://bitpoll.mafiasi.de"
WHITEBOARD_URL = "https://spacedeck.mafiasi.de"
KANBOARD_URL = "https://kanboard.mafiasi.de"
MATRIX_URL = "https://matrix.mafiasi.de"
LINK_SHORTENER_URL = "https://l.mafiasi.de"

if REGISTER_ENABLED:
    PKS_COMMUNITY_DOMAINS = REGISTER_DOMAINS + ["studium.uni-hamburg.de"]
else:
    PKS_COMMUNITY_DOMAINS = ALLOWED_HOSTS

MAILINGLIST_DOMAIN = "group.mafiasi.de"
MAILINGLIST_SERVER = ("0.0.0.0", 2522)
MAILCLOAK_DOMAIN = "cloak.mafiasi.de"
MAILCLOAK_SERVER = ("0.0.0.0", 2523)
VALID_EMAIL_ADDRESSES = ["postmaster@mafiasi.de"]
EMAIL_ADDRESSES_PASSWORD = env.str("MAFIASI_EMAIL_ADDRESSES_PASSWORD")

TEAM_EMAIL = "ag-server@informatik.uni-hamburg.de"
EMAIL_HOST = env.str("MAFIASI_EMAIL_HOST")
DEFAULT_FROM_EMAIL = "Mafiasi.de <ag-server@informatik.uni-hamburg.de>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = "[mafiasi.de] "
MAIL_SIGNATURE = "mafiasi.de-Team"

MAIL_GREETING_EN = """
Best regards,

Your Server-AG"""

MAIL_GREETING_DE = """
Grüße,

Deine Server-AG"""

MAIL_INCLUDE_GERMAN = True
INVALID_MAIL_DOMAIN = "invalid.invalid"

GUEST_EXTENSION = ".guest"
DEFAULT_GUEST_GROUP = ""
GUEST_INVITE_HINT = "Must start with a letter and only contain alphanumeric characters. Lowercase only."
GUEST_ACCEPT_INVITATION_MAIL = False

GUEST_INVITE_INSTRUCTION_LINK = "https://dash.crossmodal-learning.org/static_redir/instruction"

OAUTH2_PROVIDER = {
    "PKCE_REQUIRED": False,
}

SENTRY_DSN = env.str("SENTRY_DSN", default=None)
if SENTRY_DSN is not None:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
