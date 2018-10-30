"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from os.path import join,dirname
import django_heroku
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','4*#imhn)c@7k^e7r4)a(qw^f^+p&go8#8!tj%+$3u+u$7(h1-%')
#Other relevant env variables
SPOT_SECRET_ID=os.environ.get('SPOT_SECRET_ID')
SPOT_CLIENT_ID=os.environ.get('SPOT_CLIENT_ID')
SPOT_CALLBACK=os.environ.get('SPOT_CALLBACK')
PG_PASSWORD=os.environ.get('PG_PASSWORD')
SONGKICK_KEY=os.environ.get('SONGKICK_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DJANGO_DEBUG', True))

ALLOWED_HOSTS = ['festivalpickr.herokuapps.com','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'festivalpickr.apps.FestivalpickrConfig',
    'localflavor',
    'django_coinpayments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #'NAME': 'ecomproject',
        #'USER': 'ecomprojectuser',
        #'PASSWORD': PG_PASSWORD,
        #'HOST': 'localhost',
        #'PORT': '',
    #}
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
#STATICFILES_DIRS = [
    #os.path.join(BASE_DIR, "static")
#]

#login redirect
LOGIN_REDIRECT_URL = '/'

COINPAYMENTS_ADMIN_ENABLED = True
# Insert your API keys here
COINPAYMENTS_API_KEY = '791c8d12e23fbd6adac0f4cd520f231ff75b5f93a04866d39300dd203f06a397'
COINPAYMENTS_API_SECRET = 'E07310f10704606F08b807eA1D6EA9376D046Da108Afce66c93E0b9c3ea86cE2'

# has EOS - overrides choices for 'currency_original' and 'currency_paid' in Payment model
COINPAYMENTS_ACCEPTED_COINS = (
    ('BTC', 'Bitcoin'), ('ETH', 'Ethereum')
)

#https redirect
SECURE_SSL_REDIRECT = False

#email stuff
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'festivalpickr'
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_PASSWORD')
EMAIL_USE_TLS = True

django_heroku.settings(locals())
