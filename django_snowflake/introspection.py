from collections import namedtuple

from django.db.backends.base.introspection import (
    BaseDatabaseIntrospection, FieldInfo as BaseFieldInfo,
    TableInfo as BaseTableInfo,
)
from django.utils.regex_helper import _lazy_re_compile

FieldInfo = namedtuple('FieldInfo', BaseFieldInfo._fields + ('pk', 'comment'))
TableInfo = namedtuple('TableInfo', BaseTableInfo._fields + ('comment',))
collation_re = _lazy_re_compile(r"^VARCHAR\(\d+\) COLLATE '([\w+\-]+)'$")
field_size_re = _lazy_re_compile(r'^[A-Z]+\((\d+)\)')
precision_and_scale_re = _lazy_re_compile(r'^NUMBER\((\d+),(\d+)\)$')


def get_collation(name):
    """
    Return the collation from a "VARCHAR(11) COLLATE 'collation'" type name.
    """
    m = collation_re.search(name)
    return m[1] if m else None


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
        'TIMESTAMP_LTZ': 'DateTimeField',
        'VARCHAR': 'CharField',
        'VARIANT': 'JSONField',
    }

    def get_constraints(self, cursor, table_name):
        table_name = self.connection.ops.quote_name(table_name)
        constraints = {}
        # Foreign keys
        cursor.execute(f'SHOW IMPORTED KEYS IN TABLE {table_name}')
        for row in cursor.fetchall():
            constraints[self.identifier_converter(row[12])] = {
                'columns': [self.identifier_converter(row[8])],
                'primary_key': False,
                'unique': False,
                'foreign_key': (self.identifier_converter(row[3]), self.identifier_converter(row[4])),
                'check': False,
                'index': False,
            }
        # Primary keys
        cursor.execute(f'SHOW PRIMARY KEYS IN TABLE {table_name}')
        for row in cursor.fetchall():
            constraints[self.identifier_converter(row[6])] = {
                'columns': [self.identifier_converter(row[4])],
                'primary_key': True,
                'unique': False,
                'foreign_key': None,
                'check': False,
                'index': False,
            }
        # Unique constraints
        cursor.execute(f'SHOW UNIQUE KEYS IN TABLE {table_name}')
        # The columns of multi-column unique indexes are ordered by row[5].
        # Map {constraint_name: [(row[5], column_name), ...] so the columns can
        # be sorted for each constraint.
        unique_column_orders = {}
        for row in cursor.fetchall():
            column_name = self.identifier_converter(row[4])
            constraint_name = self.identifier_converter(row[6])
            if constraint_name in constraints:
                # If the constraint name is already present, this is a
                # multi-column unique constraint.
                constraints[constraint_name]['columns'].append(column_name)
                unique_column_orders[constraint_name].append((row[5], column_name))
            else:
                constraints[constraint_name] = {
                    'columns': [column_name],
                    'primary_key': False,
                    'unique': True,
                    'foreign_key': None,
                    'check': False,
                    'index': False,
                }
                unique_column_orders[constraint_name] = [(row[5], column_name)]
        # Order the columns of multi-column unique indexes.
        for constraint_name, orders in unique_column_orders.items():
            constraints[constraint_name]['columns'] = [col for _, col in sorted(orders)]
        return constraints

    def get_primary_key_column(self, cursor, table_name):
        pks = [field.name for field in self.get_table_description(cursor, table_name) if field.pk]
        return pks[0] if pks else None

    def get_relations(self, cursor, table_name):
        """
        Return a dictionary of {field_name: (field_name_other_table, other_table)}
        representing all foreign keys in the given table.
        """
        table_name = self.connection.ops.quote_name(table_name)
        cursor.execute(f'SHOW IMPORTED KEYS IN TABLE {table_name}')
        return {
            self.identifier_converter(row[8]): (self.identifier_converter(row[4]), self.identifier_converter(row[3]))
            for row in cursor.fetchall()
        }

    def get_field_type(self, data_type, description):
        field_type = super().get_field_type(data_type, description)
        # 16777216 is the default size if max_length isn't specified.
        if data_type == 'VARCHAR' and description.display_size == 16777216:
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
                self.identifier_converter(name),  # name
                get_data_type(data_type),  # type_code
                get_field_size(data_type),  # display_size
                None,  # internal_size
                *get_precision_and_scale(data_type),  # precision, scale
                null == 'Y',  # null_ok
                default,  # default
                get_collation(data_type),  # collation
                pk == 'Y',  # pk
                comment,  # comment
            )
            for (
                name, data_type, kind, null, default, pk, unique_key, check,
                # *_ ignores policy_name, privacy_domain, and any future
                # columns in DESCRIBE TABLE output.
                expression, comment, *_
            ) in table_info
        ]

    def identifier_converter(self, name):
        # Add quotes around Snowflake generated constraint names like
        # SYS_CONSTRAINT_e8775210-b2d4-4947-b382-c57cecc6bb6d to preserve
        # casing.
        if name.startswith("SYS_CONSTRAINT_"):
            return f'"{name}"'
        # TODO: If the identifier field isn't uppercase, then it needs to be
        # quoted to preserve its case.
        # https://github.com/Snowflake-Labs/django-snowflake/issues/43
        # This may require some changes in Django itself to work properly. This
        # would replace the special handling of SYS_CONSTRAINT_ above.
        # if name != name.upper():
        #    return f'"{name}"'
        # Otherwise, the identifier name can be lowercased for use as a model
        # field name, for example. DatabaseOperations.quote_name() reverses
        # this transformation by uppercasing the name.
        return name.lower()

    def get_table_list(self, cursor):
        cursor.execute('SHOW TABLES')
        tables = [
            TableInfo(
                self.identifier_converter(row[1]),  # table name
                't',  # 't' for table
                row[5],  # comment
            ) for row in cursor.fetchall()
        ]
        cursor.execute('SHOW VIEWS')
        views = [
            TableInfo(
                self.identifier_converter(row[1]),   # view name
                'v',  # 'v' for view
                row[6],  # comment
            ) for row in cursor.fetchall()
        ]
        return tables + views
