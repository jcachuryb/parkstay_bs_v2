import os
import confy
import sys
from django.contrib.messages import constants as messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
confy.read_environment_file(BASE_DIR+"/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)
from ledger_api_client.settings_base import *

ROOT_URLCONF = 'parkstay.urls'
SITE_ID = 1

# number of seconds before expiring a temporary booking
BOOKING_TIMEOUT = 1800 

INSTALLED_APPS += [
    'webtemplate_dbca',
#    'bootstrap3',
    'parkstay',
    'taggit',
    'rest_framework',
    'rest_framework_gis',
    'django_summernote',
    'ledger_api_client',
#    'django_site_queue',
    'appmonitor_client',
    'crispy_bootstrap5',
    'crispy_forms',

]

MIDDLEWARE_CLASSES += [
    'parkstay.middleware.BookingTimerMiddleware',
    'parkstay.middleware.CacheControl',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    #'wagov_utils.components.debug.middleware.DebugControl',
]

SESSION_COOKIE_HTTPONLY=True
# maximum number of days allowed for a booking
PS_MAX_BOOKING_LENGTH = 28 

# minimum number of remaining campsites to trigger an availaiblity warning
PS_CAMPSITE_COUNT_WARNING = 10

# number of days before clearing un unpaid booking
PS_UNPAID_BOOKING_LAPSE_DAYS = 5

WSGI_APPLICATION = 'parkstay.wsgi.application'
#MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
#        'parkstay.perms.OfficerPermission',
    ),
}

# disable Django REST Framework UI on prod
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer',)
else:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer','rest_framework_csv.renderers.CSVRenderer')


TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'parkstay', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'django_site_queue', 'templates'))
TEMPLATES[0]['OPTIONS']['context_processors'].append('parkstay.context_processors.parkstay_url')

#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'parkstay', 'cache'),
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }
}

STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'static')))
#STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'ledger_api_client', 'static')))


BPAY_ALLOWED = env('BPAY_ALLOWED',False)

OSCAR_BASKET_COOKIE_OPEN = 'parkstay_basket'


CRON_CLASSES = [
    'parkstay.cron.UnpaidBookingsReportCronJob',
    'appmonitor_client.cron.CronJobAppMonitorClient',    
]

# Additional logging for parkstay
LOGGING['loggers']['booking_checkout'] = {
    'handlers': ['console'],
    'level': 'INFO'
}

LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['file'],
    'level': 'DEBUG',
    'propagate': True, 
}

## To see database sql queries
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'handlers': {
#        'file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': str(BASE_DIR)+'/logs/sql.log',
#        },
#    },
#    'loggers': {
#        'django.db.backends': {
#            'handlers': ['file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#    },
#}

os.environ['LEDGER_REFUND_TRANSACTION_CALLBACK_MODULE'] = 'parkstay:parkstay.api.refund_transaction_callback'
os.environ['LEDGER_INVOICE_TRANSACTION_CALLBACK_MODULE'] = 'parkstay:parkstay.api.invoice_callback'
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

SYSTEM_NAME = env('SYSTEM_NAME', 'Parkstay WA')
EMAIL_FROM = env('EMAIL_FROM', ADMINS[0])
DEFAULT_FROM_EMAIL = EMAIL_FROM
WAITING_QUEUE_ENABLED = env('WAITING_QUEUE_ENABLED',"False")
QUEUE_GROUP_NAME = env('QUEUE_GROUP_NAME', None)
QUEUE_WAITING_URL = env('QUEUE_WAITING_URL', None)

PS_PAYMENT_SYSTEM_ID = env('PS_PAYMENT_SYSTEM_ID', 'S483')
if not VALID_SYSTEMS:
    VALID_SYSTEMS = [PS_PAYMENT_SYSTEM_ID]
EXPLORE_PARKS_URL = env('EXPLORE_PARKS_URL', 'https://parks.dpaw.wa.gov.au/park-stay')
PARKS_EXTERNAL_BOOKING_URL =env('PARKS_EXTERNAL_BOOKING_URL','https://parkstaybookings.dbca.wa.gov.au')
PARKSTAY_EXTERNAL_URL = env('PARKSTAY_EXTERNAL_URL','https://parkstay.dbca.wa.gov.au')
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
#LEDGER_REFUND_EMAIL = env('LEDGER_REFUND_EMAIL', False )
os.environ['LEDGER_REFUND_EMAIL'] = 'True'
VERSION_NO = '3.12'
# Only change if you make changes to Booking Properties
BOOKING_PROPERTY_CACHE_VERSION='v1.04'
QUEUE_DOMAIN = env('QUEUE_DOMAIN','')
QUEUE_URL = env('QUEUE_URL','')
QUEUE_BACKEND_URL = env('QUEUE_BACKEND_URL','')
QUEUE_ACTIVE_HOSTS = env('QUEUE_ACTIVE_HOSTS','')
ENABLE_QUEUE_MIDDLEWARE = env('ENABLE_QUEUE_MIDDLEWARE',False)
if ENABLE_QUEUE_MIDDLEWARE is True or ENABLE_QUEUE_MIDDLEWARE == 'True':
    MIDDLEWARE_CLASSES += [
        'parkstay.queue_middleware.QueueControl',
    ]

# Use git commit hash for purging cache in browser for deployment changes
GIT_COMMIT_HASH = ''
GIT_COMMIT_DATE = ''
if  os.path.isdir(BASE_DIR+'/.git/') is True:
    GIT_COMMIT_DATE = os.popen('cd '+BASE_DIR+' ; git log -1 --format=%cd').read()
    GIT_COMMIT_HASH = os.popen('cd  '+BASE_DIR+' ; git log -1 --format=%H').read()
if len(GIT_COMMIT_HASH) == 0:
    GIT_COMMIT_HASH = os.popen('cat /app/git_hash').read()
    if len(GIT_COMMIT_HASH) == 0:
       print ("ERROR: No git hash provided")
LEDGER_TEMPLATE = 'bootstrap5'

ALERT_URL=env('ALERT_URL','')
LEGACY_BOOKING_URL=env('LEGACY_BOOKING_URL','')
CAMPSITE_BOOKING_API_KEY = env('CAMPSITE_BOOKING_API_KEY','')

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = env('SESSION_FILE_PATH', '/app/session_store/')

DATA_STORE = env('DATA_STORE', os.path.join(BASE_DIR, 'data_store'))
if os.path.isdir(DATA_STORE):
    pass
else:
    os.mkdir(DATA_STORE)

#LEDGER_UI_ACCOUNTS_MANAGEMENT = [
#            {'first_name': {'options' : {'view': True, 'edit': True}}},
#            {'last_name': {'options' : {'view': True, 'edit': True}}},
#            {'residential_address': {'options' : {'view': True, 'edit': True}}},
#            {'phone_number' : {'options' : {'view': True, 'edit': True}}},
#            {'mobile_number' : {'options' : {'view': True, 'edit': True}}},
#]
# for am in LEDGER_UI_ACCOUNTS_MANAGEMENT:
#     LEDGER_UI_ACCOUNTS_MANAGEMENT_KEYS.append(list(am.keys())[0])
    

LEDGER_UI_CARDS_MANAGEMENT = True
BOOKING_PREFIX="PB"
MIDDLEWARE = MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = None

DEFAULT_SEARCH_AVAILABILITY_LOCATION=env('DEFAULT_SEARCH_AVAILABILITY_LOCATION','')

SESSION_COOKIE_AGE = 3600
DEBUG_CONTROL = False

APPLICATION_VERSION = env("APPLICATION_VERSION", "1.0.0") + "-" + GIT_COMMIT_HASH[:7]
RUNNING_DEVSERVER = len(sys.argv) > 1 and sys.argv[1] == "runserver"

# Sentry settings
SENTRY_DSN = env("SENTRY_DSN", default=None)
SENTRY_SAMPLE_RATE = env("SENTRY_SAMPLE_RATE", default=1.0)  # Error sampling rate
SENTRY_TRANSACTION_SAMPLE_RATE = env(
    "SENTRY_TRANSACTION_SAMPLE_RATE", default=0.0
)  # Transaction sampling
if not RUNNING_DEVSERVER and SENTRY_DSN and EMAIL_INSTANCE:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        sample_rate=SENTRY_SAMPLE_RATE,
        traces_sample_rate=SENTRY_TRANSACTION_SAMPLE_RATE,
        environment=EMAIL_INSTANCE.lower(),
        release=APPLICATION_VERSION,
    )

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
