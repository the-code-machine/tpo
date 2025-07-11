"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ef&%b-wh!4a=9tdq0*v7i7@81(7#5+-+nc1#zj%q7amreiu^s^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['13.51.206.99', 'api.paperbill.in','127.0.0.1']

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://paperbill.in",
    
]

CORS_ALLOW_ALL_ORIGINS = True

# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'jazzmin',
    'customer',
    'sync',
    'subscription', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Increase file upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 300 * 1024 * 1024   # 300 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 300 * 1024 * 1024   # 300 MB

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    "site_title": "Baniya Bandhu",
    "site_header": "Baniya Bandhu",
    "site_brand": "Baniya Bandhu",
    "site_logo": "images/logo.png",
"site_logo_classes": "img-fluid",
    "site_logo_height": "40px",
    "site_logo_width": "40px",
    "login_logo": "images/logo.png",            # Same or separate logo for login
    "login_logo_height": "120px",               # You control the login size

    "welcome_sign": "Welcome to Baniya Bandhu Admin",
    "copyright": "Baniya Bandhu",
    "search_model": ["auth.User", "customer.Customer"],

    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "customer"},
        {"app": "subscription"},
    ],

"icons": {
    "auth": "fas fa-users-cog",
    "auth.user": "fas fa-user",
    "auth.Group": "fas fa-users",

    "customer": "fas fa-user-tie",
    "customer.Employer": "fas fa-user-shield",
    "customer.Customer": "fas fa-address-book",

    "subscription": "fas fa-receipt",
    "subscription.Subscription": "fas fa-file-invoice-dollar",
    "subscription.Plan": "fas fa-cubes", 
    "subscription.ExecutableFile": "fas fa-settings", 
},

"custom_css": "css/custom_admin.css",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
}

# settings.py

RAZORPAY_KEY_ID = "rzp_live_s08Fs11gxQUjcB"
RAZORPAY_KEY_SECRET = "QWQpT3hx1pW4c0ByegyJGl1I"

