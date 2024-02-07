# Changelog

## 5.0.1 - 2024-02-07

* Fixed crash in `DatabaseIntrospection.get_table_description()` due to
  Snowflake adding a column to the output of `DESCRIBE TABLE` in behavior
  change bundle 2023_08.

## 5.0 - 2023-12-16

Initial release for Django 5.0.x.
