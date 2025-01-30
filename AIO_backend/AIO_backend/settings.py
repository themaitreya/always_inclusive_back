"""
Django settings for AIO_backend project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# 도메인별 SMTP config
EMAIL_CONFIGS = {
    'gmail.com': {
        'HOST': 'smtp.gmail.com',
        'PORT': 587,
        'USER': os.getenv('GMAIL_USER'),
        'PASSWORD': os.getenv('GMAIL_PASSWORD'),
        'USE_TLS': True,
    },
    'naver.com': {
        'HOST': 'smtp.naver.com',
        'PORT': 587,
        'USER': os.getenv('NAVER_USER'),
        'PASSWORD': os.getenv('NAVER_PASSWORD'),
        'USE_TLS': True,
    },
    'daum.net': {
        'HOST': 'smtp.daum.net',
        'PORT': 465,
        'USER': os.getenv('DAUM_USER'),
        'PASSWORD': os.getenv('DAUM_PASSWORD'),
        'USE_SSL': True,  # 예: 다음은 SSL 465 포트일 수도 있음
    }
}

# 기본값(혹은 fallback)
DEFAULT_EMAIL_CONFIG = {
    'HOST': 'smtp.gmail.com',
    'PORT': 587,
    'USER': os.getenv('GMAIL_USER'),
    'PASSWORD': os.getenv('GMAIL_PASSWORD'),
    'USE_TLS': True,
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vs$(3_nfpo2lrl(-f)k0-6d&gb+nw=a0e^n0zs)$hkw*^mf#b)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '34.227.17.183',   # EC2 퍼블릭 IP
    '127.0.0.1',      
    'localhost',
    '43.201.26.159',
    '13.209.47.60',
    'whatever-ott.com',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # DRF
    'rest_framework',
    
    # TokenAuthentication 사용 시
    'rest_framework.authtoken',

    # CORS
    'corsheaders',

    # 내가 만든 앱
    'accounts',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'AIO_backend.urls'

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

CORS_ALLOW_ALL_ORIGINS = True

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

WSGI_APPLICATION = 'AIO_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# # 수호님
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  # MariaDB도 mysql 엔진 사용
#         'NAME': 'test',                   # DB 이름
#         'USER': 'root',                     # DB 사용자
#         'PASSWORD': '0530',             # DB 비밀번호
#         'HOST': '127.0.0.1',                   # DB 서버 주소
#         'PORT': '3306',                        # DB 포트 (기본 3306)
#     }
# }

# 승환님 환경
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  # MariaDB도 mysql 엔진 사용
#         'NAME': 'ott_project',                   # DB 이름
#         'USER': 'root',                     # DB 사용자
#         'PASSWORD': '1234',             # DB 비밀번호
#         'HOST': '',                   # DB 서버 주소
#         'PORT': '3305',                        # DB 포트 (기본 3306)
#     }
# }

# # 준석
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # MariaDB도 mysql 엔진 사용
        'NAME': 'ott_project',                   # DB 이름
        'USER': 'root',                     # DB 사용자
        'PASSWORD': '1234',             # DB 비밀번호
        'HOST': '127.0.0.1',                   # DB 서버 주소
        'PORT': '3306',                        # DB 포트 (기본 3306)
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
