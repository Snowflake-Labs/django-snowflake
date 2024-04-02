from django.db.models.expressions import Exists


def exists(self, compiler, connection):
    # Remove the "LIMIT 1" that Django adds to EXISTS subqueries since
    # Snowflake doesn't support it.
    # https://docs.snowflake.com/en/user-guide/querying-subqueries#limitations
    self.query.clear_limits()
    return self.as_sql(compiler, connection)


def register_expressions():
    Exists.as_snowflake = exists
