from django.db import InterfaceError
from django.db.backends.base.features import BaseDatabaseFeatures
from django.utils.functional import cached_property


class DatabaseFeatures(BaseDatabaseFeatures):
    # Specifying a pk of zero is problematic because of the SELECT MAX(id)
    # approach to getting the last insert id.
    allows_auto_pk_0 = False
    can_clone_databases = True
    closed_cursor_error_class = InterfaceError
    create_test_procedure_without_params_sql = """
        CREATE PROCEDURE test_procedure() RETURNS varchar LANGUAGE JAVASCRIPT AS $$
           var i = 1;
    $$"""
    create_test_procedure_with_int_param_sql = """
        CREATE OR REPLACE PROCEDURE test_procedure(value integer) RETURNS varchar LANGUAGE PYTHON
            HANDLER = 'run'
            RUNTIME_VERSION = '3.8'
            PACKAGES = ('snowflake-snowpark-python')
        AS
        $$def run(session, value): pass
    $$"""
    # This feature is specific to the Django fork used for testing.
    enforces_foreign_key_constraints = False
    # This feature is specific to the Django fork used for testing.
    enforces_unique_constraints = False
    allows_multiple_constraints_on_same_fields = False
    has_json_object_function = False
    indexes_foreign_keys = False
    nulls_order_largest = True
    # At least for DecimalField, Snowflake errors with "Default value data type
    # does not match data type for column" if the default isn't serialized.
    requires_literal_defaults = True
    supported_explain_formats = {'JSON', 'TABULAR', 'TEXT'}
    supports_comments = True
    supports_comments_inline = True
    supports_column_check_constraints = False
    supports_table_check_constraints = False
    supports_expression_indexes = False
    supports_ignore_conflicts = False
    # This feature is specific to the Django fork used for testing.
    supports_indexes = False
    supports_index_column_ordering = False
    supports_json_field_contains = False
    # This feature is specific to the Django fork used for testing.
    supports_limit_in_exists = False
    supports_over_clause = True
    supports_partial_indexes = False
    # https://docs.snowflake.com/en/sql-reference/functions-regexp.html#backreferences
    supports_regex_backreferencing = False
    supports_sequence_reset = False
    supports_slicing_ordering_in_compound = True
    supports_subqueries_in_group_by = False
    supports_temporal_subtraction = True
    supports_transactions = True
    # This feature is specific to the Django fork used for testing.
    supports_tz_offsets = False
    supports_virtual_generated_columns = True
    uses_savepoints = False
    ignores_table_name_case = True
    test_collations = {
        'ci': 'en-ci',
        # Snowflake: case-sensitive always returns the lowercase version of a
        # letter before the uppercase version of the same letter which isn't
        # what CollateTests.test_collate_order_by_cs expects.
        'cs': None,
        'non_default': 'en-ci',
        'swedish_ci': 'sv-ci',
        'virtual': None,
    }
    test_now_utc_template = 'SYSDATE()'

    django_test_expected_failures = {
        # Subquery issue to be investigated.
        'lookup.tests.LookupTests.test_exact_exists',
        'lookup.tests.LookupQueryingTests.test_filter_exists_lhs',
        # "Binding data in type (event) is not supported." To be investigated.
        'model_fields.test_charfield.TestCharField.test_assignment_from_choice_enum',
        # Binding data in type (safestring) is not supported.
        'i18n.tests.TestModels.test_safestr',
        # Invalid argument types for function '+': (INTERVAL, TIMESTAMP_NTZ(9))
        'expressions.tests.FTimeDeltaTests.test_delta_add',
        # DatabaseOperations.format_for_duration_arithmetic() INTERVAL syntax
        # doesn't accept column names.
        'annotations.tests.NonAggregateAnnotationTestCase.test_mixed_type_annotation_date_interval',
        'expressions.tests.FTimeDeltaTests.test_datetime_and_duration_field_addition_with_annotate_and_no_output_field',  # noqa
        'expressions.tests.FTimeDeltaTests.test_datetime_and_durationfield_addition_with_filter',
        'expressions.tests.FTimeDeltaTests.test_duration_with_datetime',
        'expressions.tests.FTimeDeltaTests.test_durationfield_add',
        'expressions.tests.FTimeDeltaTests.test_durationfield_multiply_divide',
        # Interval math off by one hour due to crossing daylight saving time.
        'expressions.tests.FTimeDeltaTests.test_delta_update',
        # Altering Integer PK to AutoField not supported.
        'migrations.test_operations.OperationTests.test_alter_field_pk',
        'schema.tests.SchemaTests.test_alter_int_pk_to_autofield_pk',
        'schema.tests.SchemaTests.test_alter_int_pk_to_bigautofield_pk',
        'schema.tests.SchemaTests.test_alter_smallint_pk_to_smallautofield_pk',
        # Interval math with NULL crashes:
        # https://github.com/Snowflake-Labs/django-snowflake/issues/26
        'expressions.tests.FTimeDeltaTests.test_date_subtraction',
        'expressions.tests.FTimeDeltaTests.test_datetime_subtraction',
        'expressions.tests.FTimeDeltaTests.test_time_subtraction',
        # Invalid expression [(SELECT (MAX(U0.NUM_EMPLOYEES)) + 1 AS
        # "NEW_NUM_EMPLOYEES" FROM EXPRESSIONS_COMPANY AS U0 GROUP BY U0.ID,
        # ...  ORDER BY U0.NUM_EMPLOYEES DESC NULLS FIRST LIMIT 1 OFFSET 0)]
        # in VALUES clause.
        'expressions.tests.BasicExpressionsTests.test_object_create_with_f_expression_in_subquery',
        # JSONField queries with complex JSON parameters don't work:
        # https://github.com/Snowflake-Labs/django-snowflake/issues/58
        # Query:
        #   WHERE "MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE" = 'null'
        # needs to operate as:
        #   WHERE "MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE" = PARSE_JSON('null')
        'model_fields.test_jsonfield.TestSaveLoad.test_json_null_different_from_sql_null',
        # Query:
        #   WHERE TO_JSON("MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE":k) = '{"l": "m"}'
        # needs to operate as:
        #   WHERE TO_JSON("MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE":k) = PARSE_JSON('{"l": "m"}')
        'model_fields.test_jsonfield.TestQuerying.test_shallow_lookup_obj_target',
        # Query:
        #   WHERE "MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE" = '{"a": "b", "c": 14}'
        # needs to operate as:
        #   WHERE "MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE" = PARSE_JSON('{"a": "b", "c": 14}')
        'model_fields.test_jsonfield.TestQuerying.test_exact_complex',
        # Three cases:
        #     lookup='value__bar__in', value=[['foo', 'bar']]
        #     lookup='value__bar__in', value=[['foo', 'bar'], ['a']]
        #     lookup='value__bax__in', value=[{'foo': 'bar'}, {'a': 'b'}]
        # Query:
        #   WHERE TO_JSON("MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE":bar) IN ('["foo", "bar"]')
        # needs to operate as:
        #   WHERE TO_JSON("MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE":bar) IN (PARSE_JSON('["foo", "bar"]'))
        'model_fields.test_jsonfield.TestQuerying.test_key_in',
        # Invalid argument types for function 'GET': (VARCHAR(14), VARCHAR(3))
        'constraints.tests.CheckConstraintTests.test_validate_jsonfield_exact',
        'model_fields.test_jsonfield.TestQuerying.test_literal_annotation_filtering',
        # This isn't compatible with the SELECT ... FROM VALUES workaround
        # for inserting JSON data. In other words, this query doesn't work:
        # SELECT parse_json($1) FROM VALUES (DEFAULT);
        'schema.tests.SchemaTests.test_db_default_output_field_resolving',
        # QuerySet.bulk_update() not supported for JSONField:
        # Expression type does not match column data type, expecting VARIANT
        # but got VARCHAR(16777216) for column JSON_FIELD
        'queries.test_bulk_update.BulkUpdateTests.test_json_field',
        # Server-side bug?
        # CAST(TO_JSON("MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE":d) AS VARIANT)
        # gives '"[\\"e\\",{\\"f\\":\\"g\\"}]"' and appending [0] gives None.
        # The expected result ('"e"') is given by:
        # PARSE_JSON(TO_JSON("MODEL_FIELDS_NULLABLEJSONMODEL"."VALUE":d))[0]
        # Possibly this backend could rewrite CAST(... AS VARIANT) to PARSE_JSON(...)?
        'model_fields.test_jsonfield.TestQuerying.test_key_transform_annotation_expression',
        'model_fields.test_jsonfield.TestQuerying.test_key_transform_expression',
        'model_fields.test_jsonfield.TestQuerying.test_nested_key_transform_annotation_expression',
        'model_fields.test_jsonfield.TestQuerying.test_nested_key_transform_expression',
        # Fixed if TO_JSON is removed from the ORDER BY clause (or may be fine
        # as is as some databases give the ordering that Snowflake does.)
        'model_fields.test_jsonfield.TestQuerying.test_ordering_by_transform',
        # SQL compilation error: <subquery> is not a valid order by expression.
        'ordering.tests.OrderingTests.test_orders_nulls_first_on_filtered_subquery',
        # Zero pk validation not added yet.
        'backends.tests.MySQLPKZeroTests.test_zero_as_autoval',
        'bulk_create.tests.BulkCreateTests.test_zero_as_autoval',
        # Snowflake returns 'The Name::42.00000'.
        'db_functions.text.test_concat.ConcatTests.test_concat_non_str',
    }

    django_test_skips = {
        'Snowflake does not enforce FOREIGN KEY constraints.': {
            'backends.tests.FkConstraintsTests',
            'fixtures_regress.tests.TestFixtures.test_loaddata_raises_error_when_fixture_has_invalid_foreign_key',
            'model_fields.test_uuid.TestAsPrimaryKeyTransactionTests.test_unsaved_fk',
            'transactions.tests.NonAutocommitTests.test_orm_query_after_error_and_rollback',
        },
        'Snowflake does not enforce UNIQUE constraints.': {
            'auth_tests.test_basic.BasicTestCase.test_unicode_username',
            'auth_tests.test_migrations.ProxyModelWithSameAppLabelTests.test_migrate_with_existing_target_permission',
            'constraints.tests.UniqueConstraintTests.test_database_constraint',
            'contenttypes_tests.test_operations.ContentTypeOperationsTests.test_content_type_rename_conflict',
            'contenttypes_tests.test_operations.ContentTypeOperationsTests.test_existing_content_type_rename',
            'custom_pk.tests.CustomPKTests.test_unique_pk',
            'force_insert_update.tests.ForceInsertInheritanceTests.test_force_insert_with_existing_grandparent',
            'get_or_create.tests.GetOrCreateTestsWithManualPKs.test_create_with_duplicate_primary_key',
            'get_or_create.tests.GetOrCreateTestsWithManualPKs.test_savepoint_rollback',
            'get_or_create.tests.GetOrCreateThroughManyToMany.test_something',
            'get_or_create.tests.UpdateOrCreateTests.test_manual_primary_key_test',
            'get_or_create.tests.UpdateOrCreateTestsWithManualPKs.test_create_with_duplicate_primary_key',
            'model_fields.test_filefield.FileFieldTests.test_unique_when_same_filename',
            'one_to_one.tests.OneToOneTests.test_multiple_o2o',
            'queries.test_bulk_update.BulkUpdateTests.test_database_routing_batch_atomicity',
        },
        'Snowflake does not support indexes.': {
            'introspection.tests.IntrospectionTests.test_get_constraints_index_types',
            'migrations.test_operations.OperationTests.test_add_index',
            'migrations.test_operations.OperationTests.test_alter_field_with_index',
            'migrations.test_operations.OperationTests.test_remove_index',
            'migrations.test_operations.OperationTests.test_rename_index',
            'schema.tests.SchemaTests.test_add_remove_index',
            'schema.tests.SchemaTests.test_alter_field_add_index_to_integerfield',
            'schema.tests.SchemaTests.test_index_together',
            'schema.tests.SchemaTests.test_indexes',
            'schema.tests.SchemaTests.test_order_index',
            'schema.tests.SchemaTests.test_remove_constraints_capital_letters',
            'schema.tests.SchemaTests.test_remove_db_index_doesnt_remove_custom_indexes',
            'schema.tests.SchemaTests.test_remove_field_unique_does_not_remove_meta_constraints',
            'schema.tests.SchemaTests.test_remove_unique_together_does_not_remove_meta_constraints',
            'schema.tests.SchemaTests.test_text_field_with_db_index',
        },
        'Snowflake does not enforce PositiveIntegerField constraint.': {
            'model_fields.test_integerfield.PositiveIntegerFieldTests.test_negative_values',
        },
        'Snowflake: Unsupported subquery type cannot be evaluated.': {
            'aggregation.test_filter_argument.FilteredAggregateTests.test_filtered_aggregate_ref_multiple_subquery_annotation',  # noqa
            'aggregation.test_filter_argument.FilteredAggregateTests.test_filtered_aggregate_ref_subquery_annotation',
            'aggregation.tests.AggregateAnnotationPruningTests.test_referenced_composed_subquery_requires_wrapping',
            'aggregation.tests.AggregateAnnotationPruningTests.test_referenced_subquery_requires_wrapping',
            'aggregation.tests.AggregateTestCase.test_aggregation_subquery_annotation',
            'aggregation.tests.AggregateTestCase.test_aggregation_subquery_annotation_values',
            'annotations.tests.NonAggregateAnnotationTestCase.test_annotation_filter_with_subquery',
            'annotations.tests.NonAggregateAnnotationTestCase.test_annotation_subquery_outerref_transform',
            'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_extract_outerref',
            'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_subquery_with_parameters',
            'expressions.tests.BasicExpressionsTests.test_aggregate_subquery_annotation',
            'expressions.tests.BasicExpressionsTests.test_annotation_with_deeply_nested_outerref',
            'expressions.tests.BasicExpressionsTests.test_annotation_with_nested_outerref',
            'expressions.tests.BasicExpressionsTests.test_annotation_with_outerref',
            'expressions.tests.BasicExpressionsTests.test_annotations_within_subquery',
            'expressions.tests.BasicExpressionsTests.test_nested_outerref_with_function',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery_join_outer_ref',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery_outer_ref_2',
            'expressions.tests.BasicExpressionsTests.test_nested_subquery_outer_ref_with_autofield',
            'expressions.tests.BasicExpressionsTests.test_subquery',
            'expressions.tests.BasicExpressionsTests.test_subquery_filter_by_lazy',
            'expressions.tests.BasicExpressionsTests.test_subquery_in_filter',
            'expressions.tests.FTimeDeltaTests.test_date_subquery_subtraction',
            'expressions.tests.FTimeDeltaTests.test_datetime_subquery_subtraction',
            'expressions_window.tests.WindowFunctionTests.test_subquery_row_range_rank',
            'lookup.tests.LookupQueryingTests.test_filter_subquery_lhs',
            'lookup.tests.LookupTests.test_nested_outerref_lhs',
            'model_fields.test_jsonfield.TestQuerying.test_nested_key_transform_on_subquery',
            'model_fields.test_jsonfield.TestQuerying.test_obj_subquery_lookup',
            'queries.test_qs_combinators.QuerySetSetOperationTests.test_union_in_subquery',
            'queries.test_qs_combinators.QuerySetSetOperationTests.test_union_in_subquery_related_outerref',
            'queries.tests.ExcludeTests.test_exclude_subquery',
            'queries.tests.ExcludeTests.test_subquery_exclude_outerref',
        },
        'Snowflake: Window function type [ROW_NUMBER] requires ORDER BY in '
        'window specification.': {
             'expressions_window.tests.WindowFunctionTests.test_row_number_no_ordering',
             'prefetch_related.tests.PrefetchLimitTests.test_empty_order',
        },
        # https://github.com/Snowflake-Labs/django-snowflake/issues/40
        'DatabaseOperations.sequence_reset_sql() must be implemented for this test.': {
            'backends.tests.SequenceResetTest.test_generic_relation',
            'backends.base.test_operations.SqlFlushTests.test_execute_sql_flush_statements',
            'servers.tests.LiveServerDatabase.test_database_writes',
        },
        "Snowflake prohibits string truncation when using Cast.": {
            'db_functions.comparison.test_cast.CastTests.test_cast_to_char_field_with_max_length',
        },
        'Snowflake does not support nested transactions.': {
            'admin_changelist.tests.ChangeListTests.test_list_editable_atomicity',
            'admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_add_url_not_allowed',
            'admin_views.tests.AdminViewBasicTest.test_disallowed_to_field',
            'admin_views.tests.AdminViewPermissionsTest.test_add_view',
            'admin_views.tests.AdminViewPermissionsTest.test_change_view',
            'admin_views.tests.AdminViewPermissionsTest.test_change_view_save_as_new',
            'admin_views.tests.AdminViewPermissionsTest.test_delete_view',
            'auth_tests.test_views.ChangelistTests.test_view_user_password_is_readonly',
            'fixtures.tests.FixtureLoadingTests.test_loaddata_app_option',
            'fixtures.tests.FixtureLoadingTests.test_unmatched_identifier_loading',
            'force_insert_update.tests.ForceTests.test_force_update',
            'get_or_create.tests.GetOrCreateTests.test_get_or_create_invalid_params',
            'get_or_create.tests.UpdateOrCreateTests.test_integrity',
            'many_to_one.tests.ManyToOneTests.test_fk_assignment_and_related_object_cache',
            'many_to_many.tests.ManyToManyTests.test_add',
            'model_fields.test_booleanfield.BooleanFieldTests.test_null_default',
            'model_fields.test_floatfield.TestFloatField.test_float_validates_object',
            'multiple_database.tests.QueryTestCase.test_generic_key_cross_database_protection',
            'multiple_database.tests.QueryTestCase.test_m2m_cross_database_protection',
            'transaction_hooks.tests.TestConnectionOnCommit.test_discards_hooks_from_rolled_back_savepoint',
            'transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_rolled_back_with_outer',
            'transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_does_not_affect_outer',
        },
        'Unused DatabaseIntrospection.get_sequences() not implemented.': {
            'introspection.tests.IntrospectionTests.test_sequence_list',
        },
        'snowflake-connector-python returns datetimes with timezone': {
            'timezones.tests.LegacyDatabaseTests.test_cursor_execute_returns_naive_datetime',
        },
        'Snowflake: cannot change column type.': {
            # NUMBER to FLOAT
            'migrations.test_operations.OperationTests.test_alter_field_pk_fk',
            'migrations.test_operations.OperationTests.test_alter_fk_non_fk',
            # NUMBER to VARCHAR
            'migrations.test_executor.ExecutorTests.test_alter_id_type_with_fk',
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_fk_with_to_field_related_name_target_type_change',  # noqa
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_type_change',  # noqa
            'schema.tests.SchemaTests.test_alter_auto_field_to_char_field',
            # VARCHAR to DATE
            'schema.tests.SchemaTests.test_alter_text_field_to_date_field',
            # VARCHAR TO TIMESTAMP
            'schema.tests.SchemaTests.test_alter_text_field_to_datetime_field',
            # VARCHAR to TIME
            'schema.tests.SchemaTests.test_alter_text_field_to_time_field',
            # VARCHAR to NUMBER
            'migrations.test_operations.OperationTests.test_alter_field_pk_fk_char_to_int',
            'schema.tests.SchemaTests.test_char_field_with_db_index_to_fk',
            'schema.tests.SchemaTests.test_char_field_pk_to_auto_field',
            'schema.tests.SchemaTests.test_text_field_with_db_index_to_fk',
        },
        'Snowflake: reducing the byte-length of a varchar is not supported.': {
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_target_changes',
            'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_changes',  # noqa
            'migrations.test_operations.OperationTests.test_rename_field_reloads_state_on_fk_target_changes',
            'schema.tests.SchemaTests.test_alter_field_type_and_db_collation',
            'schema.tests.SchemaTests.test_alter_primary_key_the_same_name',
            'schema.tests.SchemaTests.test_alter_textual_field_keep_null_status',
            'schema.tests.SchemaTests.test_m2m_rename_field_in_target_model',
            'schema.tests.SchemaTests.test_rename',
        },
        'Snowflake: cannot change column type because they have incompatible collations.': {
            'migrations.test_operations.OperationTests.test_alter_field_pk_fk_db_collation',
            'schema.tests.SchemaTests.test_alter_field_db_collation',
            'schema.tests.SchemaTests.test_alter_field_type_preserve_db_collation',
            'schema.tests.SchemaTests.test_alter_primary_key_db_collation',
            'schema.tests.SchemaTests.test_ci_cs_db_collation',
        },
        # https://github.com/Snowflake-Labs/django-snowflake/issues/24
        'Database caching is not supported.': {
            'cache.tests.CreateCacheTableForDBCacheTests',
            'cache.tests.DBCacheTests',
            'cache.tests.DBCacheWithTimeZoneTests',
        },
        'assertNumQueries is sometimes off because of the extra queries this '
        'backend uses to fetch an object\'s ID.': {
            'admin_utils.test_logentry.LogEntryTests.test_log_action_fallback',
            'contenttypes_tests.test_models.ContentTypesTests.test_get_for_models_creation',
            'force_insert_update.tests.ForceInsertInheritanceTests.test_force_insert_diamond_mti',
            'force_insert_update.tests.ForceInsertInheritanceTests.test_force_insert_false',
            'force_insert_update.tests.ForceInsertInheritanceTests.test_force_insert_parent',
            'force_insert_update.tests.ForceInsertInheritanceTests.test_force_insert_with_grandparent',
            'modeladmin.tests.ModelAdminTests.test_log_deletion_fallback',
            'model_formsets_regress.tests.FormsetTests.test_extraneous_query_is_not_run',
            'model_inheritance.tests.ModelInheritanceTests.test_create_child_no_update',
            'model_inheritance.tests.ModelInheritanceTests.test_create_diamond_mti_common_parent',
        },
        'It can be problematic if a model instance is manually assigned a pk value.': {
            'contenttypes_tests.test_views.ContentTypesViewsSiteRelTests.test_shortcut_view_with_null_site_fk',
            'contenttypes_tests.test_views.ContentTypesViewsSiteRelTests.test_shortcut_view_with_site_m2m',
            'multiple_database.tests.RouterTestCase.test_m2m_cross_database_protection',
            'sites_tests.tests.SitesFrameworkTests.test_clear_site_cache_domain',
        },
        'This test takes on order of an hour due to 2,000 inserts.': {
            'delete.tests.DeletionTests.test_large_delete_related',
        },
        "Snowflake: Unsupported feature 'Alter Column Set Default'.": {
            'migrations.test_operations.OperationTests.test_alter_field_add_database_default',
            'migrations.test_operations.OperationTests.test_alter_field_change_default_to_database_default',
            'migrations.test_operations.OperationTests.test_alter_field_change_nullable_to_database_default_not_null',
            'migrations.test_operations.OperationTests.test_alter_field_change_nullable_to_decimal_database_default_not_null',  # noqa
        },
        "Snowflake: Invalid column default expression [PI()].": {
            'migrations.test_operations.OperationTests.test_add_field_database_default_function',
        },
    }

    @cached_property
    def introspected_field_types(self):
        return {
            **super().introspected_field_types,
            'DurationField': 'BigIntegerField',
            'GenericIPAddressField': 'CharField',
            'PositiveBigIntegerField': 'BigIntegerField',
            'PositiveIntegerField': 'IntegerField',
            'PositiveSmallIntegerField': 'SmallIntegerField',
        }
