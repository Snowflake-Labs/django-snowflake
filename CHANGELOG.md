# Changelog

## 4.0 - Unreleased

- Fixed crash in `DatabaseIntrospection.get_table_description()` due to
  Snowflake adding a column to the output of `DESCRIBE TABLE` in behavior
  change bundle 2023_08.

## 4.0 beta 1 - 2023-04-15

- Added support for `JSONField`.

- The `regex` lookup pattern is no longer implicitly anchored at both ends.

## 4.0 alpha 1 - 2023-02-17

Initial release for Django 4.0.x.
