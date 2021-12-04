# Snowflake backend for Django

## Install and usage

Use the version of django-snowflake that corresponds to your version of
Django. For example, to get the latest compatible release for Django 4.0.x:

`pip install django-snowflake==4.0.*`

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
        # Include 'OPTIONS' if you need to specify any other
        # snowflake.connector.connect() parameters.
        # https://docs.snowflake.com/en/user-guide/python-connector-api.html#connect
        'OPTIONS': {},
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

- `JSONField` is [not supported](https://github.com/cedar-team/django-snowflake/issues/23).

- Snowflake doesn't support check constraints, so the various
  `PositiveIntegerField` model fields allow negative values (though validation
  at the form level still works).

## Notes on Django QuerySets

* Snowflake has
  [limited support for subqueries](https://docs.snowflake.com/en/user-guide/querying-subqueries.html#types-supported-by-snowflake).

* In Snowflake, the `regex` lookup pattern is
  [implicitly anchored at both ends](https://docs.snowflake.com/en/sql-reference/functions-regexp.html#corner-cases)
  (i.e. `''` automatically becomes `'^$'`), which gives different results than
  other databases.

* Valid values for `QuerySet.explain()`'s `format` parameter are `'json'`,
  `'tabular'`, and `'text'`. The default is `'tabular'`.

## Known issues and limitations

This list isn't exhaustive. If you run into a problem, consult
`django_snowflake/features.py` to see if a similar test is skipped. Please
[create an issue on GitHub](https://github.com/cedar-team/django-snowflake/issues/new)
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
  transactions to speed it up. A future version of Django (4.1 at the earliest)
  may leverage Snowflake's single layer transactions to give some speed up.

* Interval math where the interval is a column
  [is not supported](https://github.com/cedar-team/django-snowflake/issues/27).

* Interval math with a null interval
  [crashes](https://github.com/cedar-team/django-snowflake/issues/26).
