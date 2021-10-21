import uuid

from django.db.backends.base.operations import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
    cast_char_field_without_max_length = 'varchar'
    cast_data_types = {
        'AutoField': 'NUMBER',
        'BigAutoField': 'NUMBER',
        'SmallAutoField': 'NUMBER',
    }

    def bulk_insert_sql(self, fields, placeholder_rows):
        placeholder_rows_sql = (', '.join(row) for row in placeholder_rows)
        values_sql = ', '.join('(%s)' % sql for sql in placeholder_rows_sql)
        return 'VALUES ' + values_sql

    def datetime_cast_date_sql(self, field_name, tzname):
        return '(%s)::date' % field_name

    def datetime_cast_time_sql(self, field_name, tzname):
        return '(%s)::time' % field_name

    def date_extract_sql(self, lookup_type, field_name):
        # https://docs.snowflake.com/en/sql-reference/functions-date-time.html#label-supported-date-time-parts
        if lookup_type == 'week_day':
            # For consistency across backends, return Sunday=1, Saturday=7.
            return "EXTRACT('dow', %s) + 1" % field_name
        elif lookup_type == 'iso_week_day':
            return "EXTRACT('dow_iso', %s)" % field_name
        elif lookup_type == 'iso_year':
            return "EXTRACT('yearofweekiso', %s)" % field_name
        else:
            return "EXTRACT('%s', %s)" % (lookup_type, field_name)

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        return self.date_extract_sql(lookup_type, field_name)

    def date_trunc_sql(self, lookup_type, field_name, tzname=None):
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    def time_trunc_sql(self, lookup_type, field_name, tzname=None):
        return "DATE_TRUNC('%s', %s)::time" % (lookup_type, field_name)

    def format_for_duration_arithmetic(self, sql):
        return "INTERVAL '%s MICROSECONDS'" % sql

    def get_db_converters(self, expression):
        converters = super().get_db_converters(expression)
        internal_type = expression.output_field.get_internal_type()
        if internal_type == 'UUIDField':
            converters.append(self.convert_uuidfield_value)
        return converters

    def convert_uuidfield_value(self, value, expression, connection):
        if value is not None:
            value = uuid.UUID(value)
        return value

    def last_insert_id(self, cursor, table_name, pk_name):
        # This is subject to race conditions.
        return cursor.execute(f'SELECT MAX("{pk_name}") FROM "{table_name}"').fetchone()[0]

    def quote_name(self, name):
        return '"%s"' % name.replace('.', '"."')

    def regex_lookup(self, lookup_type):
        match_option = 'c' if lookup_type == 'regex' else 'i'
        return "REGEXP_LIKE(%%s, %%s, '%s')" % match_option

    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        if not tables:
            return []
        sql = []
        if reset_sequences:
            sql.extend(
                '%s %s;' % (
                    style.SQL_KEYWORD('TRUNCATE'),
                    style.SQL_FIELD(self.quote_name(table_name)),
                ) for table_name in tables
            )
        else:
            # DELETE to preserve sequences.
            sql.extend(
                '%s %s %s;' % (
                    style.SQL_KEYWORD('DELETE'),
                    style.SQL_KEYWORD('FROM'),
                    style.SQL_FIELD(self.quote_name(table_name)),
                ) for table_name in tables
            )
        return sql
