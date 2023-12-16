# Changelog

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
