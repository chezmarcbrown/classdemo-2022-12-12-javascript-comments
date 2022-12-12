from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['www.demo.uaa490.org', 'demo.uaa490.org']

# STATIC_ROOT is only needed in production, since the Django development server
# runserver takes care of serving static files directly from your static
# directories. STATIC_ROOT is the absolute path to the directory where python
# manage.py collectstatic will collect static files for deployment.
STATIC_URL = '/static/'
STATIC_ROOT = '/home/demo490/demo.uaa490.org/public/static/'

# In deployment, the media files (i.e., files uploaded by
# the user, such as images) are not served by django,
# so they need to be where they can be accessed by the webserver.
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/demo490/demo.uaa490.org/public/media'


# In deployment, sensitive information should not be stored in github
import environ
env = environ.Env()
environ.Env.read_env()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': 'mysql.demo.uaa490.org',
        'PORT': '3306',
    }
}

#SECURE_HSTS_SECONDS = 360 
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

