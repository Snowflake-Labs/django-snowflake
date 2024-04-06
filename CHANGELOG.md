# Changelog

## 4.2.3 - 2024-04-08

* Fixed `EXISTS` subqueries by removing `LIMIT 1` (which Snowflake does not
  support) from them.

## 4.2.2 - 2024-02-23

* Fixed data corruption of new model instance IDs. Connection initialization
  now sets `NOORDER_SEQUENCE_AS_DEFAULT=False` (after [the default
  changed to True](https://docs.snowflake.com/en/release-notes/bcr-bundles/2024_01/bcr-1483)
  in behavior change bundle 2024_01) to allow this backend to continue to
  retrieve the ID of newly created objects using
  `SELECT MAX(pk_name) FROM table_name`.

## 4.2.1 - 2024-02-07

* Fixed crash in `DatabaseIntrospection.get_table_description()` due to
  Snowflake adding a column to the output of `DESCRIBE TABLE` in behavior
  change bundle 2023_08.

## 4.2 - 2023-12-15

* Bumped the minimum required version of `snowflake-connector-python` to 3.6.0.

* Fixed private key authentication with `dbshell`. For this to work, you must
  use `'private_key_file'` and`'private_key_file_pwd'` in the `'OPTIONS'`
  dictionary of the `DATABASES` setting instead of `'private_key'`. This is
  now the documented pattern in the README.

* Fixed `dbshell` crash if using the `client_session_keep_alive` or
  `passcode_in_password` options.

## 4.2 beta 1 - 2023-04-11

* Added support for `JSONField`.

## 4.2 alpha 1 - 2023-03-18

Initial release for Django 4.2.x.
