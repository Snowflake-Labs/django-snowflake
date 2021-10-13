from django.db.backends.base.features import BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    # Snowflake doesn't enforce foreign key constraints.
    supports_foreign_keys = False
    # This really means "supports_nested_transactions". Snowflake supports a
    # single level of transaction, BEGIN + (ROLLBACK|COMMIT). Multiple BEGINS
    # contribute to the current (only) transaction.
    supports_transactions = False
    uses_savepoints = False
