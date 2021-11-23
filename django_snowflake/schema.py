from django.db import NotSupportedError
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    sql_create_column_inline_fk = (
        'CONSTRAINT %(name)s FOREIGN KEY REFERENCES %(to_table)s(%(to_column)s)'
    )

    def _create_index_sql(self, model, fields=None, **kwargs):
        # Snowflake doesn't use indexes.
        return ''

    def _model_indexes_sql(self, model):
        return []

    def _field_indexes_sql(self, model, field):
        return []

    def add_index(self, model, index):
        pass

    def remove_index(self, model, index):
        pass

    def alter_index_together(self, model, old_index_together, new_index_together):
        pass

    def add_field(self, model, field):
        # Special-case implicit M2M tables
        if field.many_to_many and field.remote_field.through._meta.auto_created:
            return self.create_model(field.remote_field.through)
        # Get the column's definition
        definition, params = self.column_sql(model, field, exclude_not_null=True)
        # It might not actually have a column behind it
        if definition is None:
            return
        if field.remote_field and field.db_constraint:
            # Add FK constraint inline.
            constraint_suffix = '_fk_%(to_table)s_%(to_column)s'
            to_table = field.remote_field.model._meta.db_table
            to_column = field.remote_field.model._meta.get_field(field.remote_field.field_name).column
            definition += " " + self.sql_create_column_inline_fk % {
                'name': self._fk_constraint_name(model, field, constraint_suffix),
                'column': self.quote_name(field.column),
                'to_table': self.quote_name(to_table),
                'to_column': self.quote_name(to_column),
            }
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
        collation = getattr(field, 'db_collation', None)
        if collation:
            sql += self._collate_sql(collation)
        if not field.null and not exclude_not_null:
            sql += " NOT NULL"
        if field.primary_key:
            sql += " PRIMARY KEY"
        if field.unique:
            sql += " UNIQUE"
        return sql, []

    def _collate_sql(self, collation):
        # Collation must be single quoted instead of double quoted.
        return f" COLLATE '{collation}'"

    def _alter_field(self, model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict=False):
        super()._alter_field(
            model, old_field, new_field, old_type, new_type,
            old_db_params, new_db_params, strict,
        )
        auto_fields = self.connection.data_types_suffix
        old_internal_type = old_field.get_internal_type()
        new_internal_type = new_field.get_internal_type()
        # Altering to an AutoField isn't supported because Snowflake doesn't
        # support "ALTER COLUMN... SET DEFAULT" which would be need to add
        # a sequence to the column.
        if old_internal_type not in auto_fields and new_internal_type in auto_fields:
            raise NotSupportedError(
                "Changing field %(field_name)s to %(field_type)s isn't supported." % {
                    'field_name': old_field.name,
                    'field_type': new_internal_type,
                }
            )
        # If migrating away from AutoField, drop AUTOINCREMENT.
        if old_internal_type in auto_fields and new_internal_type not in auto_fields:
            self.execute(self.sql_alter_column % {
                "table": self.quote_name(model._meta.db_table),
                "changes": self.sql_alter_column_no_default % {
                    "column": self.quote_name(new_field.column),
                },
            })

    def quote_value(self, value):
        # A more complete implementation isn't currently required.
        return str(value)

    def skip_default_on_alter(self, field):
        # Snowflake: Unsupported feature 'Alter Column Set Default'.
        return True
