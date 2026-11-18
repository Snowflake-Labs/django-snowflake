from django.core.exceptions import FieldError
from django.db.models.expressions import Exists, Value


def exists(self, compiler, connection):
    # Remove the "LIMIT 1" that Django adds to EXISTS subqueries since
    # Snowflake doesn't support it.
    # https://docs.snowflake.com/en/user-guide/querying-subqueries#limitations
    self.query.clear_limits()
    return self.as_sql(compiler, connection)


def value(self, compiler, connection):
    sql, params = self.as_sql(compiler, connection)
    # Date and time values are sent as strings, which Snowflake treats as
    # VARCHAR. Cast them so that functions like EXTRACT accept them.
    try:
        internal_type = self.output_field.get_internal_type()
    except FieldError:
        return sql, params
    if sql == '%s' and internal_type in {'DateField', 'DateTimeField', 'TimeField'}:
        sql = f'({sql})::{self.output_field.db_type(connection)}'
    return sql, params


def register_expressions():
    Exists.as_snowflake = exists
    Value.as_snowflake = value
