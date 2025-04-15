def get_snowflake_connection() -> SnowflakeConnection:
    """Create and return a Snowflake connection with minimal testing."""
    try:
        # Create a new connection
        conn = snowflake.connector.connect(
            user=settings.SNOWFLAKE_USER,
            password=settings.SNOWFLAKE_PASSWORD,
            account=settings.SNOWFLAKE_ACCOUNT,
            warehouse=settings.SNOWFLAKE_WAREHOUSE,
            database=settings.SNOWFLAKE_DATABASE,
            schema=settings.SNOWFLAKE_SCHEMA
        )

        # Test with a very simple query that doesn't access metadata
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS test_col")
        cursor.close()

        return conn
    except Exception as e:
        logger.error(f"Error connecting to Snowflake: {str(e)}")
        raise DatabaseError(f"Database connection error: {str(e)}")