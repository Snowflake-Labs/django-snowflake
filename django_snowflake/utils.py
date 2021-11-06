import django
from django.core.exceptions import ImproperlyConfigured
from django.utils.version import get_version_tuple


def check_django_compatability():
    """
    Verify that this version of django-snowflake is compatible with the
    installed version of Django. For example, any django-snowflake 3.2.x is
    compatible with Django 3.2.y.
    """
    from . import __version__
    if django.VERSION[:2] != get_version_tuple(__version__)[:2]:
        raise ImproperlyConfigured(
            'You must use the latest version of django-snowflake {A}.{B}.x '
            'with Django {A}.{B}.y (found django-snowflake {C}).'.format(
                A=django.VERSION[0],
                B=django.VERSION[1],
                C=__version__,
            )
        )
