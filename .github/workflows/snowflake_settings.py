import os
import uuid

DATABASES = {
    'default': {
        'ENGINE': 'django_snowflake',
        'USER': os.environ['SNOWFLAKE_USER'],
        'PASSWORD': os.environ['SNOWFLAKE_PASSWORD'],
        'ACCOUNT': os.environ['SNOWFLAKE_ACCOUNT'],
        'SCHEMA': 'SCHEMA',
        'WAREHOUSE': os.environ['SNOWFLAKE_WAREHOUSE'],
        'TEST': {'NAME': 'TEST_DJANGO_' + str(uuid.uuid4()).upper()},
    },
    'other': {
        'ENGINE': 'django_snowflake',
        'USER': os.environ['SNOWFLAKE_USER'],
        'PASSWORD': os.environ['SNOWFLAKE_PASSWORD'],
        'ACCOUNT': os.environ['SNOWFLAKE_ACCOUNT'],
        'SCHEMA': 'SCHEMA',
        'WAREHOUSE': os.environ['SNOWFLAKE_WAREHOUSE'],
        'TEST': {'NAME': 'TEST_DJANGO_OTHER_' + str(uuid.uuid4()).upper()},
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
SECRET_KEY = 'django_tests_secret_key'
USE_TZ = False
