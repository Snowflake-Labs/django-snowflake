from django.db.backends.base.features import BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    has_json_object_function = False
    # Snowflake doesn't enforce foreign key constraints.
    supports_foreign_keys = False
    # Not yet implemented in this backend.
    supports_json_field = False
    supports_over_clause = True
    # https://docs.snowflake.com/en/sql-reference/functions-regexp.html#backreferences
    supports_regex_backreferencing = False
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
    }

    django_test_skips = {
        'Snowflake: Unsupported subquery type cannot be evaluated.': {
            'db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_subquery_with_parameters',
            'expressions_window.tests.WindowFunctionTests.test_subquery_row_range_rank',
            'lookup.tests.LookupTests.test_nested_outerref_lhs',
        },
        'Snowflake: Window function type [ROW_NUMBER] requires ORDER BY in '
        'window specification.': {
             'expressions_window.tests.WindowFunctionTests.test_row_number_no_ordering',
        },
        'DatabaseOperations.last_executed_query must be implemented for this test.': {
            'lookup.tests.LookupTests.test_in_ignore_none',
            'lookup.tests.LookupTests.test_in_ignore_none_with_unhashable_items',
        },
        'This test does not quote a field name in raw SQL as Snowflake requires.': {
            'lookup.tests.LookupTests.test_values',
            'lookup.tests.LookupTests.test_values_list',
        },
        "Snowflake prohibits string truncation when using Cast.": {
            'db_functions.comparison.test_cast.CastTests.test_cast_to_char_field_with_max_length',
        },
        'Time zone support not yet implemented.': {
            'db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests',
        },
    }
