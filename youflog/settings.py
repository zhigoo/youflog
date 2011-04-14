# Django settings for logpress project.
import logging
import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG
HERE = os.path.dirname(os.path.abspath(__file__))
YOUFLOG_VERSION = 0.4
ADMINS = (
     #('youflog', 'xxxx@gmail.com'),
)

logging.basicConfig(
    level = logging.INFO,
    format = '%(levelname)s %(module)s.%(funcName)s Line:%(lineno)d : %(message)s',
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.sqlite3',
        'NAME':os.path.join(HERE,'youflog.sqlite'),
    }
}

TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(HERE, 'media').replace('\\','/')

STATIC_ROOT = os.path.join(HERE, 'static').replace('\\','/')

CAPTCHA_FONT=os.path.join(HERE,'static/Vera.ttf')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/upload/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '33ukrm_%_r9!)(o4&#3)=*9411$dfqehfgg**h0rlf^)2$63kc'

CACHE_PREFIX='youflog_cache'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'blog.middleware.youflog.RpcMiddleware',
    'blog.middleware.youflog.VersionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'youflogprocessor.side',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request', 
    'django.core.context_processors.debug', 
    #'django.core.context_processors.i18n', 
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
   os.path.join(HERE,'templates'),
)

AUTH_PROFILE_MODULE='blog.UserProfile'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'blog',
    'blog.comments',
    'tagging',
    'pingback',
)

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'minhao123@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxxxx'
EMAIL_PORT = 587
