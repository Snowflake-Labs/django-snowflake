# Snowflake backend for Django

## Install and usage

Use the version of django-snowflake that corresponds to your version of
Django. For example, to get the latest compatible release for Django 4.2.x:

`pip install django-snowflake==4.2.*`

The minor release number of Django doesn't correspond to the minor release
number of django-snowflake. Use the latest minor release of each.

If a release series of django-snowflake only has pre-releases (alphas or
betas), you'll see an error with a list of the available versions. In that
case, include `--pre` to allow `pip` to install the latest pre-release.

For example, if django-snowflake 4.2 alpha 1 is the latest available version
of the 4.2 release series:

```
$ pip install django-snowflake==4.2.*
ERROR: Could not find a version that satisfies the requirement
django-snowflake==4.2.* (from versions: ..., 4.2a1)

$ pip install --pre django-snowflake==4.2.*
...
Successfully installed ... django-snowflake-4.2a1 ...
```

Configure the Django `DATABASES` setting similar to this:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_snowflake',
        'NAME': 'MY_DATABASE',
        'SCHEMA': 'MY_SCHEMA',
        'WAREHOUSE': 'MY_WAREHOUSE',
        'USER': 'my_user',
        'PASSWORD': 'my_password',
        'ACCOUNT': 'my_account',
        # Include 'OPTIONS' if you need to specify any other
        # snowflake.connector.connect() parameters, documented at:
        # https://docs.snowflake.com/en/user-guide/python-connector-api.html#connect
        'OPTIONS': {
            # Examples:
            'role': 'MY_ROLE',
            # To use native Okta authenticators:
            # https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-use#native-sso-okta-only
            'authenticator': 'https://example.okta.com',
            # To use private key authentication:
            'private_key_file': '<path>/rsa_key.p8',
            'private_key_file_pwd': 'my_passphrase',
        },
    },
}
```

## Notes on Django fields

- Consistent with [Snowflake's convention](https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html),
  this backend uppercases all database identifiers (table names, column names,
  etc.) unless they are quoted, e.g. `db_table='"table_name"'`.

- Snowflake supports defining foreign key and unique constraints, however, it
  doesn't enforce them. Thus, Django manages these constraints and `inspectdb`
  detects them, but Django won't raise `IntegrityError` if they're violated.

- Snowflake doesn't support indexes. Thus, Django ignores any indexes defined
  on models or fields.

- Snowflake doesn't support check constraints, so the various
  `PositiveIntegerField` model fields allow negative values (though validation
  at the form level still works).

## Notes on Django QuerySets

* Snowflake has
  [limited support for subqueries](https://docs.snowflake.com/en/user-guide/querying-subqueries.html#types-supported-by-snowflake).

* Valid values for `QuerySet.explain()`'s `format` parameter are `'json'`,
  `'tabular'`, and `'text'`. The default is `'tabular'`.

## Known issues and limitations

This list isn't exhaustive. If you run into a problem, consult
`django_snowflake/features.py` to see if a similar test is skipped. Please
[create an issue on GitHub](https://github.com/Snowflake-Labs/django-snowflake/issues/new)
if you encounter an issue worth documenting.

* Snowflake doesn't support `last_insert_id` to retrieve the ID of a newly
  created object. Instead, this backend issues the query
  `SELECT MAX(pk_name) FROM table_name` to retrieve the ID. This is subject
  to race conditions if objects are created concurrently. This makes this
  backend inappropriate for use in web app use cases where multiple clients
  could be creating objects at the same time. Further, you should not manually
  specify an ID (e.g. `MyModel(id=1)`) when creating an object.

* Snowflake only supports single layer transactions, but Django's `TestCase`
  requires that the database supports nested transactions. Therefore, Django's
  `TestCase` operates like `TransactionTestCase`, without the benefit of
  transactions to speed it up. A future version of Django (5.0 at the earliest)
  may leverage Snowflake's single layer transactions to give some speed up.

* Due to snowflake-connector-python's [lack of VARIANT support](https://github.com/snowflakedb/snowflake-connector-python/issues/244),
  some `JSONField` queries with complex JSON parameters [don't work](https://github.com/Snowflake-Labs/django-snowflake/issues/58).

  For example, if `value` is a `JSONField`, this won't work:
  ```python
  >>> JSONModel.objects.filter(value__k={"l": "m"})
  ```
  A workaround is:
  ```python
  >>> from django.db.models.expressions import RawSQL
  >>> JSONModel.objects.filter(value__k=RawSQL("PARSE_JSON(%s)", ('{"l": "m"}',)))
  ```
  In addition, ``QuerySet.bulk_update()`` isn't supported for `JSONField`.

* Interval math where the interval is a column
  [is not supported](https://github.com/Snowflake-Labs/django-snowflake/issues/27).

* Interval math with a null interval
  [crashes](https://github.com/Snowflake-Labs/django-snowflake/issues/26).

## Troubleshooting

### Debug logging

To troubleshoot issues with connectivity to Snowflake, you can enable
[Snowflake Connector for Python's logging](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example#logging)
using [Django's `LOGGING` setting](https://docs.djangoproject.com/en/4.2/topics/logging/).

This is a minimal addition to Django's default `"loggers"` configuration that
enables the connector's `DEBUG` logging:

```python
LOGGING = {
    …
    "loggers": {
        …
        "snowflake.connector": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}
```
