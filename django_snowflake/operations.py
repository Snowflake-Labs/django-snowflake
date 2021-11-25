import decimal
import uuid

from django.conf import settings
from django.db.backends.base.operations import BaseDatabaseOperations
from django.utils import timezone


class DatabaseOperations(BaseDatabaseOperations):
    cast_char_field_without_max_length = 'varchar'
    cast_data_types = {
        'AutoField': 'NUMBER',
        'BigAutoField': 'NUMBER',
        'SmallAutoField': 'NUMBER',
    }
    explain_prefix = 'EXPLAIN USING'

    def bulk_insert_sql(self, fields, placeholder_rows):
        placeholder_rows_sql = (', '.join(row) for row in placeholder_rows)
        values_sql = ', '.join('(%s)' % sql for sql in placeholder_rows_sql)
        return 'VALUES ' + values_sql

    def combine_expression(self, connector, sub_expressions):
        lhs, rhs = sub_expressions
        if connector == '&':
            return 'BITAND(%s)' % ','.join(sub_expressions)
        elif connector == '|':
            return 'BITOR(%(lhs)s,%(rhs)s)' % {'lhs': lhs, 'rhs': rhs}
        elif connector == '#':
            return 'BITXOR(%(lhs)s, %(rhs)s)' % {'lhs': lhs, 'rhs': rhs}
        elif connector == '<<':
            return 'BITSHIFTLEFT(%(lhs)s, %(rhs)s)' % {'lhs': lhs, 'rhs': rhs}
        elif connector == '>>':
            return 'BITSHIFTRIGHT(%(lhs)s, %(rhs)s)' % {'lhs': lhs, 'rhs': rhs}
        elif connector == '^':
            return 'POWER(%s)' % ','.join(sub_expressions)
        return super().combine_expression(connector, sub_expressions)

    def _convert_field_to_tz(self, field_name, tzname):
        if tzname and settings.USE_TZ:
            field_name = "CONVERT_TIMEZONE('%s', TO_TIMESTAMP(%s))" % (
                tzname,
                field_name,
            )
        return field_name

    def datetime_cast_date_sql(self, field_name, tzname):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return '(%s)::date' % field_name

    def datetime_cast_time_sql(self, field_name, tzname):
        field_name = self._convert_field_to_tz(field_name, tzname)
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
        field_name = self._convert_field_to_tz(field_name, tzname)
        return self.date_extract_sql(lookup_type, field_name)

    def date_trunc_sql(self, lookup_type, field_name, tzname=None):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    def time_trunc_sql(self, lookup_type, field_name, tzname=None):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return "DATE_TRUNC('%s', %s)::time" % (lookup_type, field_name)

    def format_for_duration_arithmetic(self, sql):
        return "INTERVAL '%s MICROSECONDS'" % sql

    def get_db_converters(self, expression):
        converters = super().get_db_converters(expression)
        internal_type = expression.output_field.get_internal_type()
        if internal_type == 'DateTimeField':
            if not settings.USE_TZ:
                converters.append(self.convert_datetimefield_value)
        elif internal_type == 'UUIDField':
            converters.append(self.convert_uuidfield_value)
        return converters

    def convert_datetimefield_value(self, value, expression, connection):
        if value is not None:
            # Django expects naive datetimes when settings.USE_TZ is False.
            value = timezone.make_naive(value)
        return value

    def convert_durationfield_value(self, value, expression, connection):
        # Snowflake sometimes returns Decimal which is an unsupported type for
        # timedelta microseconds component.
        if isinstance(value, decimal.Decimal):
            value = float(value)
        return super().convert_durationfield_value(value, expression, connection)

    def convert_uuidfield_value(self, value, expression, connection):
        if value is not None:
            value = uuid.UUID(value)
        return value

    def adapt_datetimefield_value(self, value):
        # Work around a bug in Django: https://code.djangoproject.com/ticket/33229
        if hasattr(value, 'resolve_expression'):
            return value
        return super().adapt_datetimefield_value(value)

    def adapt_timefield_value(self, value):
        # Work around a bug in Django: https://code.djangoproject.com/ticket/33229
        if hasattr(value, 'resolve_expression'):
            return value
        return super().adapt_timefield_value(value)

    def explain_query_prefix(self, format=None, **options):
        if format is None:
            format = 'TABULAR'
        prefix = super().explain_query_prefix(format, **options)
        return prefix + ' ' + format

    def last_insert_id(self, cursor, table_name, pk_name):
        # This is subject to race conditions.
        return cursor.execute(
            'SELECT MAX({pk_name}) FROM {table_name}'.format(
                pk_name=self.quote_name(pk_name),
                table_name=self.quote_name(table_name),
            )
        ).fetchone()[0]

    def limit_offset_sql(self, low_mark, high_mark):
        # This method is copied from BaseDatabaseOperations with 'LIMIT %d'
        # replaced with 'LIMIT %s' to allow "LIMIT null" for no limit.
        limit, offset = self._get_limit_offset_params(low_mark, high_mark)
        return ' '.join(sql for sql in (
            ('LIMIT %s' % limit) if limit else None,
            ('OFFSET %d' % offset) if offset else None,
        ) if sql)

    def no_limit_value(self):
        return 'null'

    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
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

    def subtract_temporals(self, internal_type, lhs, rhs):
        lhs_sql, lhs_params = lhs
        rhs_sql, rhs_params = rhs
        if internal_type == 'TimeField':
            # Cast rhs_sql with TO_TIME in case it's a string.
            return f"TIMEDIFF(MICROSECOND, TO_TIME({rhs_sql}), {lhs_sql})", (*rhs_params, *lhs_params)
        return f"TIMEDIFF(MICROSECOND, {rhs_sql}, {lhs_sql})", (*rhs_params, *lhs_params)
