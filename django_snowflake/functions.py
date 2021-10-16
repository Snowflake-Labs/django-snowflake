from django.db.models.functions import (
    SHA224, SHA256, SHA384, SHA512, ConcatPair, StrIndex,
)


def concatpair(self, compiler, connection, **extra_context):
    # coalesce() prevents Concat from returning null instead of empty string.
    return self.coalesce().as_sql(compiler, connection, **extra_context)


def strindex(self, compiler, connection, **extra_context):
    # POSITION takes arguments in the opposite order of other databases.
    # https://docs.snowflake.com/en/sql-reference/functions/position.html
    return StrIndex(
        self.source_expressions[1],
        self.source_expressions[0],
    ).as_sql(compiler, connection, function='POSITION', **extra_context)


def register_functions():
    SHA224.as_snowflake = SHA224.as_mysql
    SHA256.as_snowflake = SHA256.as_mysql
    SHA384.as_snowflake = SHA384.as_mysql
    SHA512.as_snowflake = SHA512.as_mysql
    ConcatPair.as_snowflake = concatpair
    StrIndex.as_snowflake = strindex
