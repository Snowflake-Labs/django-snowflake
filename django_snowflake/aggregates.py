from django.db.models.aggregates import BitAnd, BitOr, BitXor, StringAgg


def bit_and(self, compiler, connection, **extra_context):
    return self.as_sql(compiler, connection, function="BIT_AND_AGG", **extra_context)


def bit_or(self, compiler, connection, **extra_context):
    return self.as_sql(compiler, connection, function="BIT_OR_AGG", **extra_context)


def bit_xor(self, compiler, connection, **extra_context):
    return self.as_sql(compiler, connection, function="BIT_XOR_AGG", **extra_context)


def string_agg(self, compiler, connection, **extra_context):
    return self.as_sql(compiler, connection, function="LISTAGG", **extra_context)


def register_aggregates():
    BitAnd.as_snowflake = bit_and
    BitOr.as_snowflake = bit_or
    BitXor.as_snowflake = bit_xor
    StringAgg.as_snowflake = string_agg
