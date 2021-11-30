from django.core.exceptions import ImproperlyConfigured
from django.db.backends.base.base import BaseDatabaseWrapper
from django.utils.asyncio import async_unsafe

try:
    import snowflake.connector as Database
except ImportError as e:
    raise ImproperlyConfigured("Error loading snowflake connector module: %s" % e)

# Some of these import snowflake connector, so import them after checking if it's installed.
from .client import DatabaseClient                          # NOQA isort:skip
from .creation import DatabaseCreation                      # NOQA isort:skip
from .features import DatabaseFeatures                      # NOQA isort:skip
from .introspection import DatabaseIntrospection            # NOQA isort:skip
from .operations import DatabaseOperations                  # NOQA isort:skip
from .schema import DatabaseSchemaEditor                    # NOQA isort:skip


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'snowflake'
    display_name = 'Snowflake'
    data_types = {
        'AutoField': 'NUMBER(10,0)',
        'BigAutoField': 'NUMBER(38,0)',
        'BinaryField': 'BINARY',
        'BooleanField': 'BOOLEAN',
        'CharField': 'VARCHAR(%(max_length)s)',
        'DateField': 'DATE',
        'DateTimeField': 'TIMESTAMP_LTZ',
        'DecimalField': 'NUMBER(%(max_digits)s,%(decimal_places)s)',
        'DurationField': 'NUMBER(38,0)',
        'FileField': 'VARCHAR(%(max_length)s)',
        'FilePathField': 'VARCHAR(%(max_length)s)',
        'FloatField': 'FLOAT',
        'IntegerField': 'NUMBER(10,0)',
        'BigIntegerField': 'NUMBER(38,0)',
        'GenericIPAddressField': 'VARCHAR(39)',
        'JSONField': 'VARIANT',
        'NullBooleanField': 'BOOLEAN',
        'OneToOneField': 'NUMBER(38,0)',
        'PositiveBigIntegerField': 'NUMBER(38,0)',
        'PositiveIntegerField': 'NUMBER(10,0)',
        'PositiveSmallIntegerField': 'NUMBER(5,0)',
        'SlugField': 'VARCHAR(%(max_length)s)',
        'SmallAutoField': 'NUMBER(5,0)',
        'SmallIntegerField': 'NUMBER(5,0)',
        'TextField': 'VARCHAR',
        'TimeField': 'TIME',
        'UUIDField': 'VARCHAR(32)',
    }
    data_types_suffix = {
        'AutoField': 'AUTOINCREMENT',
        'BigAutoField': 'AUTOINCREMENT',
        'SmallAutoField': 'AUTOINCREMENT',
    }
    operators = {
        'exact': '= %s',
        'iexact': "ILIKE %s ESCAPE '\\\\'",
        'contains': "LIKE %s ESCAPE '\\\\'",
        'icontains': "ILIKE %s ESCAPE '\\\\'",
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': "LIKE %s ESCAPE '\\\\'",
        'endswith': "LIKE %s ESCAPE '\\\\'",
        'istartswith': "ILIKE %s ESCAPE '\\\\'",
        'iendswith': "ILIKE %s ESCAPE '\\\\'",
    }
    pattern_esc = r"{}"  # TODO: complete this expression
    pattern_ops = {
        'contains': "LIKE '%%' || {} || '%%'",
        'icontains': "ILIKE '%%' || {} || '%%'",
        'startswith': "LIKE {} || '%%'",
        'istartswith': "ILIKE {} || '%%'",
        'endswith': "LIKE '%%' || {}",
        'iendswith': "ILIKE '%%' || {}",
    }

    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor

    # Classes instantiated in __init__().
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations

    settings_is_missing = "settings.DATABASES is missing '%s' for 'django_snowflake'."

    def get_connection_params(self):
        settings_dict = self.settings_dict
        conn_params = {}

        if settings_dict['NAME']:
            conn_params['database'] = self.ops.quote_name(settings_dict['NAME'])

        if settings_dict['USER']:
            conn_params['user'] = settings_dict['USER']
        else:
            raise ImproperlyConfigured(self.settings_is_missing % 'USER')

        if settings_dict['PASSWORD']:
            conn_params['password'] = settings_dict['PASSWORD']
        else:
            raise ImproperlyConfigured(self.settings_is_missing % 'PASSWORD')

        if settings_dict.get('ACCOUNT'):
            conn_params['account'] = settings_dict['ACCOUNT']
        else:
            raise ImproperlyConfigured(self.settings_is_missing % 'ACCOUNT')

        if settings_dict.get('WAREHOUSE'):
            conn_params['warehouse'] = self.ops.quote_name(settings_dict['WAREHOUSE'])
        else:
            raise ImproperlyConfigured(self.settings_is_missing % 'WAREHOUSE')

        if settings_dict.get('ROLE'):
            conn_params['role'] = self.ops.quote_name(settings_dict['ROLE'])

        if settings_dict.get('SCHEMA'):
            conn_params['schema'] = self.ops.quote_name(settings_dict['SCHEMA'])
        else:
            raise ImproperlyConfigured(self.settings_is_missing % 'SCHEMA')

        return conn_params

    @async_unsafe
    def get_new_connection(self, conn_params):
        return Database.connect(**conn_params)

    def ensure_timezone(self):
        if self.connection is None:
            return False
        with self.connection.cursor() as cursor:
            conn_timezone_name = cursor.execute("SHOW PARAMETERS LIKE 'TIMEZONE'").fetchone()[1]
        timezone_name = self.timezone_name
        if timezone_name and conn_timezone_name != timezone_name:
            with self.connection.cursor() as cursor:
                cursor.execute("ALTER SESSION SET TIMEZONE=%s", [timezone_name])
            return True
        return False

    def init_connection_state(self):
        timezone_changed = self.ensure_timezone()
        if timezone_changed:
            # Commit after setting the time zone (see #17062)
            # (This is copied from the postgresql backend.)
            if not self.get_autocommit():
                self.connection.commit()

    @async_unsafe
    def create_cursor(self, name=None):
        return self.connection.cursor()

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit(autocommit)

    def is_usable(self):
        try:
            # Use a cursor directly, bypassing Django's utilities.
            with self.connection.cursor() as cursor:
                cursor.execute('SELECT current_version()')
        except Database.Error:
            return False
        else:
            return True
