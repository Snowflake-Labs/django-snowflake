from django.db import DatabaseError
from django.db.backends.base.features import BaseDatabaseFeatures
from django.utils.functional import cached_property


class DatabaseFeatures(BaseDatabaseFeatures):
    can_clone_databases = True
    can_introspect_json_field = False
    # This should be InterfaceError:
    # https://github.com/snowflakedb/snowflake-connector-python/issues/943
    closed_cursor_error_class = DatabaseError
    has_case_insensitive_like = False
    has_json_object_function = False
    supports_column_check_constraints = False
    supports_table_check_constraints = False
    supports_ignore_conflicts = False
    supports_index_column_ordering = False
    # Not yet implemented in this backend.
    supports_json_field = False
    supports_over_clause = True
    supports_partial_indexes = False
    # https://docs.snowflake.com/en/sql-reference/functions-regexp.html#backreferences
    supports_regex_backreferencing = False
    supports_sequence_reset = False
    supports_subqueries_in_group_by = False
    # This really means "supports_nested_transactions". Snowflake supports a
    # single level of transaction, BEGIN + (ROLLBACK|COMMIT). Multiple BEGINS
    # contribute to the current (only) transaction.
    supports_transactions = False
    uses_savepoints = False

    django_test_expected_failures = {
        # Subquery issue to be investigated.
        'lookup.tests.LookupTests.test_exact_exists',
        # In Snowflake "the regex pattern is implicitly anchored at both ends
        # (i.e. '' automatically becomes '^$')." This gives different results
        # than other databases.
        # https://docs.snowflake.com/en/sql-reference/functions-regexp.html#corner-cases
        'lookup.tests.LookupTests.test_regex',
        # "Snowflake's RANDOM() returns a 64-bit integer, but Django expects [0, 1.0)"
        'db_functions.math.test_random.RandomTests.test',
        # "Binding data in type (event) is not supported." To be investigated.
        'model_fields.test_charfield.TestCharField.test_assignment_from_choice_enum',
        # Violating NOT NULL constraint should raise IntegrityError instead of
        # ProgrammingError: https://github.com/snowflakedb/snowflake-connector-python/issues/922
        'model_fields.test_booleanfield.BooleanFieldTests.test_null_default',
        # Invalid argument types for function '+': (INTERVAL, TIMESTAMP_NTZ(9))
        'expressions.tests.FTimeDeltaTests.test_delta_add',
        # DatabaseOperations.format_for_duration_arithmetic() INTERVAL syntax
        # doesn't accept column names.
        'annotations.tests.NonAggregateAnnotationTestCase.test_mixed_type_annotation_date_interval',
        'expressions.tests.FTimeDeltaTests.test_duration_with_datetime',
        'expressions.tests.FTimeDeltaTests.test_durationfield_add',
        # Interval math off by one microsecond for years beyond ~2250:
        # https://github.com/snowflakedb/snowflake-connector-python/issues/926
        'expressions.tests.FTimeDeltaTests.test_duration_with_datetime_microseconds',
        # DatabaseWrapper.pattern_esc not implemented.
        'expressions.tests.ExpressionsTests.test_insensitive_patterns_escape',
        'expressions.tests.ExpressionsTests.test_patterns_escape',
        # Cursor.execute() raises an exception rather than passing silently if
        # params is empty:
        # https://github.com/snowflakedb/snowflake-connector-python/issues/939
        'backends.tests.BackendTestCase.test_cursor_executemany_with_empty_params_list',
        # Cursor.execute() crashes with iterators:
        # https://github.com/snowflakedb/snowflake-connector-python/issues/939
        'backends.tests.BackendTestCase.test_cursor_executemany_with_iterator',
        'backends.tests.BackendTestCase.test_cursor_executemany_with_pyformat_iterator',
        # TypeError: unsupported type for timedelta microseconds component:
        # decimal.Decimal
        'aggregation.tests.AggregateTestCase.test_avg_duration_field',
    }

    django_test_skips = {
        'BinaryField support blocked on https://github.com/snowflakedb/snowflake-connector-python/issues/907': {
            'backends.tests.LastExecutedQueryTest.test_query_encoding',
            'bulk_create.tests.BulkCreateTests.test_bulk_insert_nullable_fields',
            'bulk_create.tests.BulkCreateTests.test_nullable_fk_after_parent',
            'model_fields.test_binaryfield.BinaryFieldTests',
        },
        'Snowflake does not enforce FOREIGN KEY constraints.': {
            'backends.tests.FkConstraintsTests',
            'model_fields.test_uuid.TestAsPrimaryKeyTransactionTests.test_unsaved_fk',
        },
        'Snowflake does not enforce UNIQUE constraints.': {
            'model_fields.test_filefield.FileFieldTests.test_unique_when_same_filename',
            'one_to_one.tests.OneToOneTests.test_multiple_o2o',
        },
        'Snowflake does not support indexes.': {
            'introspection.tests.IntrospectionTests.test_get_constraints_index_types',
        },
        'Snowflake does not enforce PositiveIntegerField constraint.': {
            'model_fields.test_integerfield.PositiveIntegerFieldTests.test_negative_values',
        },
        'Snowflake: Unsupported subquery type cannot be evaluated.': {
            'aggregation.test_filter_argument.FilteredAggregateTests.test_filtered_aggregate_ref_multiple_subquery_annotation',  # noqa
            'aggregation.test_filter_argument.FilteredAggregateTests.test_filtered_aggregate_ref_subquery_annotation',
            'aggregation.tests.AggregateTestCase.test_aggregation_subquery_annotation',
            'aggregation.tests.AggregateTestCase.test_aggregation_subquery_annotation_values',
            'aggregation.tests.AggregateTestCase.test_aggregation_subquery_annotation_values_collision',
            'aggregation_regress.tests.AggregationTests.test_annotate_and_join',
            'annotations.tests.NonAggregateAnnotationTestCase.test_annotation_exists_aggregate_values_chaining',
            'annotations.tests.NonAggregateAnnotationTestCase.test_annotation_filter_with_subquery',
            'annotations.tests.NonAggregateAnnotationTestCase.test_annotation_subquery_outerref_transform',
            'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_subquery_with_parameters',
            'expressions_window.tests.WindowFunctionTests.test_subquery_row_range_rank',
            'lookup.tests.LookupTests.test_nested_outerref_lhs',
            'expressions.tests.BasicExpressionsTests.test_aggregate_subquery_annotation',
            'expressions.tests.BasicExpressionsTests.test_annotation_with_nested_outerref',
            'expressions.tests.BasicExpressionsTests.test_annotation_with_outerref',
            'expressions.tests.BasicExpressionsTests.test_annotations_within_subquery',
            'expressions.tests.BasicExpressionsTests.test_boolean_expression_combined',
            'expressions.tests.BasicExpressionsTests.test_boolean_expression_combined_with_empty_Q',
            'expressions.tests.BasicExpressionsTests.test_case_in_filter_if_boolean_output_field',
            'expressions.tests.BasicExpressionsTests.test_exists_in_filter',
            'expressions.tests.BasicExpressionsTests.test_nested_outerref_with_function',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery_join_outer_ref',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery_outer_ref_2',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery_outer_ref_with_autofield',
            'expressions.tests.BasicExpressionsTests.test_order_by_exists',
            'expressions.tests.BasicExpressionsTests.test_subquery',
            'expressions.tests.BasicExpressionsTests.test_subquery_filter_by_lazy',
            'expressions.tests.BasicExpressionsTests.test_subquery_in_filter',
        },
        'Snowflake: Window function type [ROW_NUMBER] requires ORDER BY in '
        'window specification.': {
             'expressions_window.tests.WindowFunctionTests.test_row_number_no_ordering',
        },
        'DatabaseOperations.last_executed_query must be implemented for this test.': {
            'backends.tests.BackendTestCase.test_queries',
            'backends.tests.LastExecutedQueryTest.test_last_executed_query',
            'backends.tests.LastExecutedQueryTest.test_last_executed_query_dict',
            'lookup.tests.LookupTests.test_in_ignore_none',
            'lookup.tests.LookupTests.test_in_ignore_none_with_unhashable_items',
        },
        'DatabaseOperations.sequence_reset_sql() must be implemented for this test.': {
            'backends.tests.SequenceResetTest.test_generic_relation',
            'backends.base.test_operations.SqlFlushTests.test_execute_sql_flush_statements',
        },
        'This test does not quote a field name in raw SQL as Snowflake requires.': {
            'aggregation_regress.tests.AggregationTests.test_annotation',
            'aggregation_regress.tests.AggregationTests.test_more_more',
            'aggregation_regress.tests.AggregationTests.test_more_more_more',
            'annotations.tests.NonAggregateAnnotationTestCase.test_raw_sql_with_inherited_field',
            'lookup.tests.LookupTests.test_values',
            'lookup.tests.LookupTests.test_values_list',
            'expressions.tests.BasicExpressionsTests.test_filtering_on_rawsql_that_is_boolean',
            'expressions.tests.BasicExpressionsTests.test_order_by_multiline_sql',
            'model_fields.test_booleanfield.BooleanFieldTests.test_return_type',
        },
        "Snowflake prohibits string truncation when using Cast.": {
            'db_functions.comparison.test_cast.CastTests.test_cast_to_char_field_with_max_length',
        },
        'Time zone support not yet implemented.': {
            'datetimes.tests.DateTimesTests.test_datetimes_ambiguous_and_invalid_times',
            'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests',
            'model_fields.test_datetimefield.DateTimeFieldTests.test_lookup_date_with_use_tz',
        },
        'Snowflake does not support nested transactions.': {
            'model_fields.test_floatfield.TestFloatField.test_float_validates_object',
        },
        'Unused DatabaseIntrospection.get_key_columns() not implemented.': {
            'introspection.tests.IntrospectionTests.test_get_key_columns',
        },
        'Unused DatabaseIntrospection.get_sequences() not implemented.': {
            'introspection.tests.IntrospectionTests.test_sequence_list',
        },
    }

    @cached_property
    def introspected_field_types(self):
        return{
            **super().introspected_field_types,
            'DurationField': 'BigIntegerField',
            'GenericIPAddressField': 'CharField',
            'PositiveBigIntegerField': 'BigIntegerField',
            'PositiveIntegerField': 'IntegerField',
            'PositiveSmallIntegerField': 'SmallIntegerField',
        }
