from functools import partial
from itertools import chain

from django.db.models import JSONField
from django.db.models.sql import compiler


class SQLInsertCompiler(compiler.SQLInsertCompiler):
    def as_sql(self):
        """Overridden to to wrap JSONField values with parse_json()."""
        # We don't need quote_name_unless_alias() here, since these are all
        # going to be column names (so we can avoid the extra overhead).
        qn = self.connection.ops.quote_name
        opts = self.query.get_meta()
        insert_statement = self.connection.ops.insert_statement(
            on_conflict=self.query.on_conflict,
        )
        result = ["%s %s" % (insert_statement, qn(opts.db_table))]
        select_columns = []
        if fields := list(self.query.fields):
            from django.db.models.expressions import DatabaseDefault

            supports_default_keyword_in_bulk_insert = (
                self.connection.features.supports_default_keyword_in_bulk_insert
            )
            value_cols = []
            has_json_field = False
            for i, field in enumerate(list(fields), 1):
                if isinstance(field, JSONField):
                    has_json_field = True
                    select_columns.append(f'parse_json(${i})')
                else:
                    select_columns.append(f'${i}')

                field_prepare = partial(self.prepare_value, field)
                field_pre_save = partial(self.pre_save_val, field)
                field_values = [
                    field_prepare(field_pre_save(obj)) for obj in self.query.objs
                ]
                if not field.has_db_default():
                    value_cols.append(field_values)
                    continue

                # If all values are DEFAULT don't include the field and its
                # values in the query as they are redundant and could prevent
                # optimizations. This cannot be done if we're dealing with the
                # last field as INSERT statements require at least one.
                if len(fields) > 1 and all(
                    isinstance(value, DatabaseDefault) for value in field_values
                ):
                    fields.remove(field)
                    continue

                if supports_default_keyword_in_bulk_insert:
                    value_cols.append(field_values)
                    continue

                # If the field cannot be excluded from the INSERT for the
                # reasons listed above and the backend doesn't support the
                # DEFAULT keyword each values must be expanded into their
                # underlying expressions.
                prepared_db_default = field_prepare(field.db_default)
                field_values = [
                    (
                        prepared_db_default
                        if isinstance(value, DatabaseDefault)
                        else value
                    )
                    for value in field_values
                ]
                value_cols.append(field_values)
            value_rows = list(zip(*value_cols))
            result.append("(%s)" % ", ".join(qn(f.column) for f in fields))

            if not has_json_field:
                select_columns = []
        else:
            # No fields were specified but an INSERT statement must include at
            # least one column. This can only happen when the model's primary
            # key is composed of a single auto-field so default to including it
            # as a placeholder to generate a valid INSERT statement.
            value_rows = [
                [self.connection.ops.pk_default_value()] for _ in self.query.objs
            ]
            fields = [None]
            result.append("(%s)" % qn(opts.pk.column))

        # Currently the backends just accept values when generating bulk
        # queries and generate their own placeholders. Doing that isn't
        # necessary and it should be possible to use placeholders and
        # expressions in bulk inserts too.
        can_bulk = (
            not self.returning_fields and self.connection.features.has_bulk_insert
        )

        placeholder_rows, param_rows = self.assemble_as_sql(fields, value_rows)

        on_conflict_suffix_sql = self.connection.ops.on_conflict_suffix_sql(
            fields,
            self.query.on_conflict,
            (f.column for f in self.query.update_fields),
            (f.column for f in self.query.unique_fields),
        )
        if (
            self.returning_fields
            and self.connection.features.can_return_columns_from_insert
        ):
            if self.connection.features.can_return_rows_from_bulk_insert:
                result.append(
                    self.connection.ops.bulk_insert_sql(fields, placeholder_rows)
                )
                params = param_rows
            else:
                result.append("VALUES (%s)" % ", ".join(placeholder_rows[0]))
                params = [param_rows[0]]
            if on_conflict_suffix_sql:
                result.append(on_conflict_suffix_sql)
            # Skip empty r_sql to allow subclasses to customize behavior for
            # 3rd party backends. Refs #19096.
            r_sql, self.returning_params = self.connection.ops.return_insert_columns(
                self.returning_fields
            )
            if r_sql:
                result.append(r_sql)
                params += [self.returning_params]
            return [(" ".join(result), tuple(chain.from_iterable(params)))]

        if select_columns:
            result.append('SELECT ' + (", ".join(c for c in select_columns)) + ' FROM')

        if can_bulk:
            result.append(self.connection.ops.bulk_insert_sql(fields, placeholder_rows))
            if on_conflict_suffix_sql:
                result.append(on_conflict_suffix_sql)
            return [(" ".join(result), tuple(p for ps in param_rows for p in ps))]
        else:
            if on_conflict_suffix_sql:
                result.append(on_conflict_suffix_sql)
            return [
                (" ".join([*result, "VALUES (%s)" % ", ".join(p)]), vals)
                for p, vals in zip(placeholder_rows, param_rows)
            ]


SQLCompiler = compiler.SQLCompiler
SQLDeleteCompiler = compiler.SQLDeleteCompiler
SQLUpdateCompiler = compiler.SQLUpdateCompiler
SQLAggregateCompiler = compiler.SQLAggregateCompiler
