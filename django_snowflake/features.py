from django.db.backends.base.features import BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    # Snowflake doesn't enforce foreign key constraints.
    supports_foreign_keys = False
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
            'lookup.tests.LookupTests.test_nested_outerref_lhs',
        },
        'DatabaseOperations.last_executed_query must be implemented for this test.': {
            'lookup.tests.LookupTests.test_in_ignore_none',
            'lookup.tests.LookupTests.test_in_ignore_none_with_unhashable_items',
        },
        'This test does not quote a field name in raw SQL as Snowflake requires.': {
            'lookup.tests.LookupTests.test_values',
            'lookup.tests.LookupTests.test_values_list',
        },
    }
