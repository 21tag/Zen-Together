# Django settings for zen_together project.
import os
from secrets import DB_NAME, DB_USER, DB_PASS, DB_PORT, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT

DEPLOY = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('The Admin', 'admin@zentogether.com'),
)

MANAGERS = ADMINS

if DEPLOY:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            #'ENGINE': 'postgresql_psycopg2_persistent',
            'NAME': DB_NAME,                      # Or path to database file if using sqlite3.
            'USER': DB_USER,                      # Not used with sqlite3.
            'PASSWORD': DB_PASS,                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': DB_PORT,                      # Set to empty string for default. Not used with sqlite3.
            'OPTIONS': {'autocommit' : True }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            #'ENGINE': 'postgresql_psycopg2_persistent',
            'NAME': 'zen.db',                      # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD':'',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
            'OPTIONS': ''
        }
    }

# GEOIP Settings
if DEPLOY:
    GEOIP_PATH = '/home/dbro/geoip'
else:
    GEOIP_PATH = '/home/dbro/geoip/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = '/home/dbro/django/zen-together2/zen_together/uploads/'
MEDIA_ROOT = '/home/dbro/prod/uploads/'
#Change this for deploymen

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/dbro/static/zt/'
#Change this for deployment

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = 'http://zentogether.com/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = 'http://zentogether.com/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'static'),
    #"/static",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'b1-yu3hi7ge!m)-9&q&5#3i^9fx-76$s1$o%%swxm%7k*j6$4d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
    'tracking.middleware.VisitorCleanUpMiddleware',
    #'tracking.middleware.VisitorCleanUpMiddleware', #clear past visitor data
)

ROOT_URLCONF = 'zen_together.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

    #allauth pals:
    'emailconfirmation',
    'uni_form',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #'allauth.twitter',
    #'allauth.openid',
    'allauth.facebook',
    'zen',
    'tracking',
    #'avatar',
    
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "allauth.context_processors.allauth",
    "allauth.account.context_processors.account",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request", #Makes request accessible to templates
    "django.core.context_processors.static",
)

AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
)

SOCIALACCOUNT_AVATAR_SUPPORT = False

AVATAR_STORAGE_DIR = 'uploads/avatars'

AVATAR_URL = AVATAR_STORAGE_DIR

LOGIN_REDIRECT_URL = ('/profile/')

AUTH_PROFILE_MODULE = 'zen.UserProfile'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

EMAIL_USE_TLS = True