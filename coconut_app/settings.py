import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-6a$y-=79j3$sem^=%eqb=e=mutfr=x)mr052n&m^0)z$$o+3i8')

DEBUG = True


ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "ec2-16-16-183-238.eu-north-1.compute.amazonaws.com",
    "coconut-app.onrender.com"
   
]



CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://ec2-16-16-183-238.eu-north-1.compute.amazonaws.com",
]
CSRF_TRUSTED_ORIGINS = [
    "http://ec2-16-16-183-238.eu-north-1.compute.amazonaws.com",
    "http://localhost", 
    "http://127.0.0.1"

]
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = False 



SITE_DOMAIN = os.getenv('SITE_DOMAIN', 'http://localhost:3000')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'coconut_calculation',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'rest_framework_simplejwt.token_blacklist',
    'allauth.socialaccount',
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
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'coconut_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'coconut_app.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Ensure this directory exists

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Ensure this directory exists

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=20),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
'''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "msanjith130@gmail.com"
EMAIL_HOST_PASSWORD = "nwne fotx cqir qkil"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
'''


import os

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "email-smtp.eu-north-1.amazonaws.com"  # ✅ AWS SES Region
EMAIL_PORT = 587  # ✅ Use 587 for TLS (recommended)
EMAIL_USE_TLS = True  # ✅ Enable TLS (Secure)
EMAIL_USE_SSL = False  # ❌ Don't use SSL with TLS

# ✅ Load SMTP Credentials from Environment Variables
EMAIL_HOST_USER = "AKIAVVZOOB6MQCEYXLE5"  # 🔒 Store in .env
EMAIL_HOST_PASSWORD ="BDUPpRKR/VcLZuQknzL3t8hVPaHlx5yvH+kqX+UJhbL1"  

DEFAULT_FROM_EMAIL = "awssanjith@gmail.com"  


FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

AUTH_USER_MODEL = "coconut_calculation.User"  # ✅ Correct user model

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # Corrected Redis Port
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Enter token as: Bearer <your_token>',
        }
    },
    'USE_SESSION_AUTH': False,
}

PHONE_EMAIL_API_URL = "https://admin.phone.email/accountdetails"  
PHONE_EMAIL_API_KEY = "ebEHNFbgNDcSUQCWaqM3PCuw4PuTaobW"  # Replace with your actual API key
PHONE_EMAIL_FROM_PHONE = "9003495946"  # The sender's phone number
PHONE_EMAIL_FROM_COUNTRY = "+91"  # Country code (change if needed)

PHONE_EMAIL_REQUEST_TIMEOUT = 10  # Timeout in seconds

# Retry Configuration
PHONE_EMAIL_MAX_RETRIES = 3  
PHONE_EMAIL_RETRY_DELAY = 5  



