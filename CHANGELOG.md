# Changelog

## 6.0.1 - 2026-08-18

- Fix crash creating virtual ``GeneratedField`` columns with a NUMBER type
  where the generated expression's inferred precision doesn't match the
  column's declared precision, e.g. when the expression involves arithmetic on
  NUMBER columns.

- Allow a user-provided ``DATABASES[...]['OPTIONS']['application']``. In older
  versions, the default value (``"Django_SnowflakeConnector_X.Y.Z"``) cannot be
  overridden.

- Added support for connecting from inside a Snowpark Container Services
  (SPCS) service. When the ``SNOWFLAKE_SERVICE_NAME`` environment variable is
  set, django-snowflake automatically uses the OAuth login token and host that
  Snowflake provides, and ``DATABASES[...]['USER']`` isn't required.

## 6.0 - 2025-12-05

Initial release for Django 6.0.x.
