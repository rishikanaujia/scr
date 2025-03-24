"""Service for handling transaction-related database operations."""
import logging
from typing import Dict, List, Any, Optional, Tuple

from app.query_builder.builder import FlexibleQueryBuilder
from app.database.connection import execute_query, execute_query_with_timeout
from app.utils.errors import QueryBuildError, DatabaseError, SchemaCompatibilityError
from app.config.settings import settings

# Import schema management if available
try:
    from app.schema_management import schema_service
    from app.utils.schema_adapter import SchemaAdapter

    SCHEMA_SERVICE_AVAILABLE = True
except ImportError:
    SCHEMA_SERVICE_AVAILABLE = False

# Setup logging
logger = logging.getLogger(__name__)


class TransactionService:
    """Service for handling transaction database operations."""

    @staticmethod
    async def execute_transaction_query(params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Build and execute a transaction query.

        Args:
            params: Dictionary of query parameters

        Returns:
            List of transaction records

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Check schema compatibility if enabled
            if (SCHEMA_SERVICE_AVAILABLE and
                    getattr(settings, 'SCHEMA_VERSION_CHECK_ON_STARTUP', False) and
                    getattr(settings, 'STRICT_SCHEMA_CHECKING', False)):

                try:
                    # Perform quick compatibility check
                    from app.schema_management.version import SchemaVersionManager
                    version_manager = SchemaVersionManager()
                    expected_hash = getattr(settings, 'EXPECTED_SCHEMA_HASH', None)

                    if expected_hash:
                        is_compatible = await version_manager.check_schema_compatibility(expected_hash)
                        if not is_compatible:
                            current_hash = await version_manager.calculate_schema_hash()
                            logger.warning(
                                f"Schema incompatibility detected! Expected: {expected_hash[:8]}..., Current: {current_hash[:8]}...")

                            if getattr(settings, 'STRICT_SCHEMA_CHECKING', False):
                                raise SchemaCompatibilityError(
                                    "Database schema has changed and is incompatible with this application version",
                                    current_hash, expected_hash
                                )
                except Exception as e:
                    logger.warning(f"Schema compatibility check failed: {str(e)}")
                    # Continue execution since this is not critical

            # Build query from request parameters
            query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
            query_builder.parse_request_params(params)
            sql_query = query_builder.build_query()

            logger.info(f"Executing transaction query: {sql_query}")

            # Check if timeout parameter is provided
            timeout = params.get('timeout')
            if timeout:
                try:
                    timeout_seconds = int(timeout)
                    results = await execute_query_with_timeout(sql_query, timeout_seconds)
                except ValueError:
                    # Invalid timeout value, use default timeout
                    results = await execute_query_with_timeout(sql_query)
            else:
                # Execute query with default timeout
                results = await execute_query(sql_query)

            return results

        except (QueryBuildError, SchemaCompatibilityError):
            # Re-raise specific errors
            raise
        except Exception as e:
            # Handle other errors
            logger.error(f"Error in transaction service: {str(e)}", exc_info=True)
            raise DatabaseError(f"Error processing transaction request: {str(e)}")

    @staticmethod
    async def execute_count_query(params: Dict[str, str]) -> int:
        """Build and execute a count query.

        Args:
            params: Dictionary of query parameters

        Returns:
            Number of matching transactions

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Build count query from request parameters
            query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
            query_builder.parse_request_params(params)
            count_query = query_builder.build_count_query()

            logger.info(f"Executing transaction count query: {count_query}")

            # Execute query
            results = await execute_query(count_query)

            # Extract count from result
            if results and len(results) > 0:
                return results[0].get('total_count', 0)
            return 0
        except QueryBuildError:
            # Re-raise query building errors
            raise
        except Exception as e:
            # Handle other errors
            logger.error(f"Error in transaction count service: {str(e)}", exc_info=True)
            raise DatabaseError(f"Error processing transaction count request: {str(e)}")

    @staticmethod
    async def get_related_companies(transaction_id: int) -> List[Dict[str, Any]]:
        """Get companies related to a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of related companies with roles
        """
        # Build query for related companies
        params = {
            "select": "crel.companyid AS companyId, c.companyname AS companyName, " +
                      "crt.transactiontocompanyreltype AS role, " +
                      "cr.percentacquired AS percentAcquired, " +
                      "si.simpleindustrydescription AS industry",
            "transactionId": str(transaction_id)
        }

        # Execute query with dynamic schema adapter
        query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
        query_builder.parse_request_params(params)

        # Ensure required joins
        query_builder.add_required_join('transaction_rel')
        query_builder.add_required_join('company_rel')
        query_builder.add_required_join('relation_type')
        query_builder.add_required_join('company')
        query_builder.add_required_join('industry')

        # Build and execute query
        sql_query = query_builder.build_query()
        results = await execute_query(sql_query)

        return results

    @staticmethod
    async def get_transaction_advisors(transaction_id: int) -> List[Dict[str, Any]]:
        """Get advisors for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of advisors with roles
        """
        # Build query for advisors
        params = {
            "select": "advcompany.companyname AS advisorName, " +
                      "at.advisortypename AS role",
            "transactionId": str(transaction_id)
        }

        # Execute query with dynamic schema adapter
        query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
        query_builder.parse_request_params(params)

        # Ensure required joins
        query_builder.add_required_join('advisor_rel')
        query_builder.add_required_join('advisory_type')
        query_builder.add_required_join('advisor_company')

        # Build and execute query
        sql_query = query_builder.build_query()
        results = await execute_query(sql_query)

        return results

    @staticmethod
    async def validate_query(params: Dict[str, str]) -> Dict[str, Any]:
        """Validate a query without executing it.

        Args:
            params: Query parameters

        Returns:
            Information about the query
        """
        try:
            # Build query without executing
            query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
            query_builder.parse_request_params(params)

            # Get the SQL query
            sql_query = query_builder.build_query()

            return {
                "valid": True,
                "sql_query": sql_query,
                "joins": [j["key"] for j in query_builder.joins],
                "select_fields": query_builder.select_fields,
                "conditions": len(query_builder.where_conditions)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "error_type": e.__class__.__name__
            }