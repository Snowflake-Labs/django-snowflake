from collections import namedtuple

from django.db.backends.base.introspection import (
    BaseDatabaseIntrospection, FieldInfo as BaseFieldInfo, TableInfo,
)
from django.utils.regex_helper import _lazy_re_compile

FieldInfo = namedtuple('FieldInfo', BaseFieldInfo._fields + ('pk',))
field_size_re = _lazy_re_compile(r'^[A-Z]+\((\d+)\)$')
precision_and_scale_re = _lazy_re_compile(r'^NUMBER\((\d+),(\d+)\)$')


def get_data_type(name):
    """Extract the data type name from an ABC(...) type name."""
    return name.split('(', 1)[0]


def get_field_size(name):
    """Extract the size number from a VARCHAR(11) type name."""
    m = field_size_re.search(name)
    return int(m[1]) if m else None


def get_precision_and_scale(name):
    """
    Return the precision (first number) and scale (second number) from a
    NUMBER(38,0) type name.
    """
    m = precision_and_scale_re.search(name)
    return (int(m[1]), int(m[2])) if m else (None, None)


class DatabaseIntrospection(BaseDatabaseIntrospection):
    # Maps Snowflake data types returned by `DESCRIBE TABLE` to Django Fields.
    data_types_reverse = {
        'BINARY': 'BinaryField',
        'BOOLEAN': 'BooleanField',
        'DATE': 'DateField',
        'FLOAT': 'FloatField',
        'NUMBER': 'BigIntegerField',
        'TIME': 'TimeField',
        'TIMESTAMP_NTZ': 'DateTimeField',
        'VARCHAR': 'CharField',
    }

    def get_primary_key_column(self, cursor, table_name):
        pks = [field.name for field in self.get_table_description(cursor, table_name) if field.pk]
        return pks[0] if pks else None

    def get_field_type(self, data_type, description):
        field_type = super().get_field_type(data_type, description)
        # 16777216 is the default size if max_length isn't specified.
        if data_type == 'VARCHAR' and description.internal_size == 16777216:
            return 'TextField'
        # Handle NUMBER if it's something besides BigAutoField.
        if data_type == 'NUMBER':
            if description.scale != 0:
                return 'DecimalField'
            elif description.precision == 5:
                field_type = 'SmallIntegerField'
            elif description.precision == 10:
                field_type = 'IntegerField'
        # Handle AutoField and variants.
        if description.default and 'IDENTITY' in description.default:
            if field_type == 'IntegerField':
                return 'AutoField'
            elif field_type == 'BigIntegerField':
                return 'BigAutoField'
            elif field_type == 'SmallIntegerField':
                return 'SmallAutoField'
        return field_type

    def get_table_description(self, cursor, table_name):
        cursor.execute('DESCRIBE TABLE %s' % self.connection.ops.quote_name(table_name))
        table_info = cursor.fetchall()
        return [
            FieldInfo(
                # name, type_code, display_size, internal_size,
                name, get_data_type(data_type), None, get_field_size(data_type),
                # precision, scale, null_ok, default,
                *get_precision_and_scale(data_type), null == 'Y', default,
                # collation, pk,
                None, pk == 'Y',
            )
            for (
                name, data_type, kind, null, default, pk, unique_key, check,
                expression, comment, policy_name,
            ) in table_info
        ]

    def get_table_list(self, cursor):
        cursor.execute('SHOW TERSE TABLES')
        tables = [TableInfo(row[1], 't') for row in cursor.fetchall()]
        cursor.execute('SHOW TERSE VIEWS')
        views = [TableInfo(row[1], 'v') for row in cursor.fetchall()]
        return tables + views
