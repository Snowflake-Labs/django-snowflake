import sys

from django.db.backends.base.creation import BaseDatabaseCreation


class DatabaseCreation(BaseDatabaseCreation):
    def _quote_name(self, name):
        return self.connection.ops.quote_name(name)

    def _database_exists(self, cursor, database_name):
        try:
            cursor.execute(f'USE DATABASE {database_name}')
        except Exception as exc:
            if 'Object does not exist, or operation cannot be performed.' in str(exc):
                return False
            raise
        return True

    def _execute_create_test_db(self, cursor, parameters, keepdb=False):
        if not keepdb or not self._database_exists(cursor, parameters['dbname']):
            # Try to create a database if keepdb=False or if keepdb=True and
            # the database doesn't exist.
            super()._execute_create_test_db(cursor, parameters, keepdb)
        schema_name = self._quote_name(self.connection.settings_dict['SCHEMA'])
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name}')

    def _clone_test_db(self, suffix, verbosity, keepdb=False):
        source_database_name = self.connection.settings_dict['NAME']
        target_database_name = self.get_test_db_clone_settings(suffix)['NAME']
        test_db_params = {
            'dbname': self._quote_name(target_database_name),
            'suffix': 'CLONE ' + self._quote_name(source_database_name),
        }
        with self._nodb_cursor() as cursor:
            try:
                self._execute_create_test_db(cursor, test_db_params, keepdb)
            except Exception:
                try:
                    if verbosity >= 1:
                        self.log('Destroying old test database for alias %s...' % (
                            self._get_database_display_str(verbosity, target_database_name),
                        ))
                    cursor.execute('DROP DATABASE %(dbname)s' % test_db_params)
                    self._execute_create_test_db(cursor, test_db_params, keepdb)
                except Exception as e:
                    self.log('Got an error cloning the test database: %s' % e)
                    sys.exit(2)
