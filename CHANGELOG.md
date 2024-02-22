# Changelog

## 3.2 - 2024-02-23

- Fixed crash in `DatabaseIntrospection.get_table_description()` due to
  Snowflake adding a column to the output of `DESCRIBE TABLE` in behavior
  change bundle 2023_08.

- Fixed data corruption of new model instance IDs. Connection initialization
  now sets `NOORDER_SEQUENCE_AS_DEFAULT=False` (after [the default
  changed to True](https://docs.snowflake.com/en/release-notes/bcr-bundles/2024_01/bcr-1483)
  in behavior change bundle 2024_01) to allow this backend to continue to
  retrieve the ID of newly created objects using
  `SELECT MAX(pk_name) FROM table_name`.

## 3.2 beta 1 - 2023-04-17

- Added support for `JSONField`.

- The `regex` lookup pattern is no longer implicitly anchored at both ends.

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
