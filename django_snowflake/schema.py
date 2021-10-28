from django.db.backends.base.schema import BaseDatabaseSchemaEditor


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    def _create_index_sql(self, model, fields=None, **kwargs):
        # Snowflake doesn't use indexes.
        return ''

    def _model_indexes_sql(self, model):
        # Snowflake doesn't use indexes.
        return []

    def _field_indexes_sql(self, model, field):
        # Snowflake doesn't use indexes.
        return []

    def quote_value(self, value):
        # A more complete implementation isn't currently required.
        return str(value)
