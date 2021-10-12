from django.db.backends.base.creation import BaseDatabaseCreation


class DatabaseCreation(BaseDatabaseCreation):
    def _execute_create_test_db(self, cursor, parameters, keepdb=False):
        super()._execute_create_test_db(cursor, parameters, keepdb)
        cursor.execute('CREATE SCHEMA IF NOT EXISTS %s' % self.connection.settings_dict['SCHEMA'])
