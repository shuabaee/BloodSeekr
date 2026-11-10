"""Isolated tests: never connect to or migrate Supabase."""
import os
import tempfile
import secrets
os.environ.setdefault('DJANGO_SECRET_KEY', secrets.token_urlsafe(48))
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
from .settings import *
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
MEDIA_ROOT = tempfile.mkdtemp(prefix='bloodseekr-test-')
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
