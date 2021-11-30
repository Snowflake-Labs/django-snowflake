# Changelog

## 3.2 alpha 2 - Unreleased

- Implemented `DatabaseOperations.last_executed_query()`.
- Install now requires snowflake-connector-python 2.7.2 (previously no minimum
  version was specified).
- Made `Cursor.execute()` interpolate SQL when `params=()`, consistent with
  other database drivers.
- Fixed pattern lookups with `F()` expressions.

## 3.2 alpha 1 - 2021-12-02

Initial release for Django 3.2.x.
