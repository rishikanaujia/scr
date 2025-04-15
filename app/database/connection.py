def get_snowflake_connection() -> SnowflakeConnection:
    """Create and return a Snowflake connection.

    Returns:
        Snowflake connection

    Raises:
        DatabaseError: If connection fails
    """
    # First check if credentials are available
    if not settings.SNOWFLAKE_USER or not settings.SNOWFLAKE_PASSWORD or not settings.SNOWFLAKE_ACCOUNT:
        logger.error("Snowflake credentials are missing. Check your .env file and environment variables.")
        raise DatabaseError("Missing Snowflake credentials. Please check your configuration.")

    # Check for available connection in the pool
    if _connection_pool:
        # First clean up any expired connections
        _cleanup_connection_pool()

        # Try to find a free connection
        for conn_entry in _connection_pool:
            if not conn_entry['in_use']:
                # Mark connection as in use
                conn_entry['in_use'] = True
                conn_entry['last_used'] = time.time()

                # Test if connection is still valid
                try:
                    conn = conn_entry['connection']
                    # Simple query to test connection with a short timeout
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()  # Actually fetch the result
                    cursor.close()
                    logger.debug("Reusing existing connection from pool")
                    return conn
                except Exception as e:
                    # Connection is stale, remove it and continue
                    logger.warning(f"Removing stale connection from pool: {str(e)}")
                    try:
                        conn_entry['connection'].close()
                    except Exception as close_error:
                        logger.debug(f"Error closing stale connection: {str(close_error)}")
                    _connection_pool.remove(conn_entry)
                    # Continue to create a new connection

    # Create a new connection
    try:
        # Log connection attempt (without credentials)
        logger.info(f"Creating new Snowflake connection to account: {settings.SNOWFLAKE_ACCOUNT}, "
                    f"database: {settings.SNOWFLAKE_DATABASE}, schema: {settings.SNOWFLAKE_SCHEMA}")

        # Try with more detailed error handling
        try:
            conn = snowflake.connector.connect(
                user=settings.SNOWFLAKE_USER,
                password=settings.SNOWFLAKE_PASSWORD,
                account=settings.SNOWFLAKE_ACCOUNT,
                warehouse=settings.SNOWFLAKE_WAREHOUSE,
                database=settings.SNOWFLAKE_DATABASE,
                schema=settings.SNOWFLAKE_SCHEMA,
                login_timeout=30,  # Add timeout to prevent hanging
                network_timeout=30  # Add network timeout
            )
        except snowflake.connector.errors.DatabaseError as sf_error:
            # Handle specific Snowflake errors
            error_msg = str(sf_error)
            if "authenticator" in error_msg.lower():
                raise DatabaseError(f"Authentication error: {error_msg}")
            elif "account" in error_msg.lower():
                raise DatabaseError(f"Account error - check account format: {error_msg}")
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                raise DatabaseError(f"Network connection error: {error_msg}")
            else:
                raise DatabaseError(f"Snowflake error: {error_msg}")

        # Test the connection with a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()  # Actually fetch the result
        cursor.close()

        # Add to pool if not full
        if len(_connection_pool) < _max_pool_size:
            _connection_pool.append({
                'connection': conn,
                'created': time.time(),
                'last_used': time.time(),
                'in_use': True
            })
            logger.debug(f"Added new connection to pool (size: {len(_connection_pool)})")
        elif all(conn_entry['in_use'] for conn_entry in _connection_pool):
            logger.warning("Connection pool is full with all connections in use")

        return conn

    except DatabaseError:
        # Re-raise DatabaseError with original message
        raise
    except Exception as e:
        logger.error(f"Error connecting to Snowflake: {str(e)}")
        raise DatabaseError(f"Database connection error: {str(e)}")