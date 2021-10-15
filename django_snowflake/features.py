from django.db.backends.base.features import BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    # Snowflake doesn't enforce foreign key constraints.
    supports_foreign_keys = False
    # This really means "supports_nested_transactions". Snowflake supports a
    # single level of transaction, BEGIN + (ROLLBACK|COMMIT). Multiple BEGINS
    # contribute to the current (only) transaction.
    supports_transactions = False
    uses_savepoints = False

    django_test_expected_failures = {
        # Subquery issue to be investigated.
        'lookup.tests.LookupTests.test_exact_exists',
        # regex lookup not yet implemented.
        'lookup.tests.LookupTests.test_regex',
        'lookup.tests.LookupTests.test_regex_backreferencing',
        'lookup.tests.LookupTests.test_regex_non_ascii',
        'lookup.tests.LookupTests.test_regex_non_string',
        'lookup.tests.LookupTests.test_regex_null',
        # text lookup escaping not implemented.
        'lookup.tests.LookupTests.test_escaping',
        'lookup.tests.LookupTests.test_exclude',
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
