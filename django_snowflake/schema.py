from django.db.backends.base.schema import BaseDatabaseSchemaEditor


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    def _model_indexes_sql(self, model):
        # Snowflake doesn't use indexes.
        return []

    def _field_indexes_sql(self, model, field):
        # Snowflake doesn't use indexes.
        return []
