import os

PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SITE_ID = 1
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(PROJECT_DIR, 'test.db')
TEMPLATE_DIRS = [os.path.join(PROJECT_DIR, 'templates')]
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.admin',
    'require_media',
]
MIDDLEWARE_CLASSES = [
    'require_media.middleware.RequireMediaMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
ROOT_URLCONF = 'testproject.urls'
MEDIA_URL = '/media/'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'require_media.context_processors.require_media',
)
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
REQUIRE_MEDIA_REQUIREMENT_GROUP_ALIASES = {
    'jquery': 'js'
}
REQUIRE_MEDIA_REQUIREMENT_ALIASES = {
    'jquery.min.js': 'jquery.js'
}
