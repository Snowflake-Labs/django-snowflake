# Changelog

## 4.1 - Unreleased

- Fixed crash in `DatabaseIntrospection.get_table_description()` due to
  Snowflake adding a column to the output of `DESCRIBE TABLE` in behavior
  change bundle 2023_08.

## 4.1 beta 1 - 2023-04-14

- Added support for `JSONField`.

- The `regex` lookup pattern is no longer implicitly anchored at both ends.

## 4.1 alpha 1 - 2023-02-20

Initial release for Django 4.1.x.
