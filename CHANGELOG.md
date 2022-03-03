# Changelog

## 3.2 alpha 2 - 2022-03-03

- Backwards incompatible: database identifiers (table names, column names,
  etc.) are now uppercased by default. If you created tables with alpha 1,
  you'll need to convert the table and column names to uppercase, or define
  quoted lowercase table and column names on all your models, e.g.
  `db_table='"table_name"'`.
- Implemented `DatabaseOperations.last_executed_query()`.
- Install now requires snowflake-connector-python 2.7.4 (previously no minimum
  version was specified).
- Made `Cursor.execute()` interpolate SQL when `params=()`, consistent with
  other database drivers.
- Fixed pattern lookups with `F()` expressions.
- Allowed specifying [snowflake.connector.connect()](https://docs.snowflake.com/en/user-guide/python-connector-api.html#connect)
  parameters using the `'OPTIONS'` dictionary in the `DATABASES` setting. The
  optional `'role'` parameter must now be passed this way rather than through
  an undocumented top-level `'ROLE'` key in `DATABASES`.

## 3.2 alpha 1 - 2021-12-02

Initial release for Django 3.2.x.
