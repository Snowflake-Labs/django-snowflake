from django.db.models.aggregates import StringAgg


def string_agg(self, compiler, connection, **extra_context):
    return self.as_sql(compiler, connection, function="LISTAGG", **extra_context)


def register_aggregates():
    StringAgg.as_snowflake = string_agg
