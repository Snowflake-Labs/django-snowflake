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

    def add_field(self, model, field):
        # Special-case implicit M2M tables
        if field.many_to_many and field.remote_field.through._meta.auto_created:
            return self.create_model(field.remote_field.through)
        # Get the column's definition
        definition, params = self.column_sql(model, field, exclude_not_null=True)
        # It might not actually have a column behind it
        if definition is None:
            return
        # Build the SQL and run it
        sql = self.sql_create_column % {
            "table": self.quote_name(model._meta.db_table),
            "column": self.quote_name(field.column),
            "definition": definition,
        }
        self.execute(sql, params)
        # Set default values on existing rows. Django usually uses database
        # defaults for this, but Snowflake doesn't allow dropping a default
        # value for columns added after the table is created.
        effective_default = self.effective_default(field)
        if effective_default is not None:
            self.execute(
                "UPDATE %(table)s SET %(column)s=%%s" % {
                    "table": self.quote_name(model._meta.db_table),
                    "column": self.quote_name(field.column),
                },
                (effective_default,),
            )
        # Add NOT NULL to the column, if required, after it's created rather
        # when it's created, otherwise a database default would be required
        # which can't be dropped as discussed in the previous comment.
        if not field.null:
            db_params = field.db_parameters(connection=self.connection)
            self.execute(
                self.sql_alter_column % {
                    "table": self.quote_name(model._meta.db_table),
                    "changes": self.sql_alter_column_not_null % {
                        "column": self.quote_name(field.column),
                        "type": db_params["type"],
                    },
                },
            )

    def column_sql(self, model, field, include_default=False, exclude_not_null=False):
        # Get the column's type and use that as the basis of the SQL
        db_params = field.db_parameters(connection=self.connection)
        sql = db_params["type"]
        # Check for fields that aren't actually columns (e.g. M2M)
        if sql is None:
            return None, None
        if not field.null and not exclude_not_null:
            sql += " NOT NULL"
        if field.primary_key:
            sql += " PRIMARY KEY"
        if field.unique:
            sql += " UNIQUE"
        return sql, []

    def quote_value(self, value):
        # A more complete implementation isn't currently required.
        return str(value)
