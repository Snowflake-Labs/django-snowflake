# Changelog

## 5.0.2 - 2024-02-23

* Fixed data corruption of new model instance IDs. Connection initialization
  now sets `NOORDER_SEQUENCE_AS_DEFAULT=False` (after [the default
  changed to True](https://docs.snowflake.com/en/release-notes/bcr-bundles/2024_01/bcr-1483)
  in behavior change bundle 2024_01) to allow this backend to continue to
  retrieve the ID of newly created objects using
  `SELECT MAX(pk_name) FROM table_name`.

## 5.0.1 - 2024-02-07

* Fixed crash in `DatabaseIntrospection.get_table_description()` due to
  Snowflake adding a column to the output of `DESCRIBE TABLE` in behavior
  change bundle 2023_08.

## 5.0 - 2023-12-16

Initial release for Django 5.0.x.
