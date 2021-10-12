# Snowflake backend for Django

## Install and usage

Use the version of django-snowflake that corresponds to your version of
Django. For example, to get the latest compatible release for Django 3.2.x:

`pip install django-snowflake==3.2.*`

The minor release number of Django doesn't correspond to the minor release
number of django-snowflake. Use the latest minor release of each.

Configure the Django `DATABASES` setting similar to this:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_snowflake',
        'NAME': 'MY_DATABASE',
        'SCHEMA': 'MY_SCHEME',
        'WAREHOUSE': 'MY_WAREHOUSE',
        'USER': 'my_user',
        'PASSWORD': 'my_password',
        'ACCOUNT': 'my_account',
    },
}
```

## Notes on Django fields

...

## Notes on Django QuerySets

...

## FAQ

...

## Known issues and limitations

...
