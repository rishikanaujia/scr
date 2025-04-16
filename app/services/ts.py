"""Transaction service for executing queries."""
import logging
from typing import Dict, List, Any, Optional

from app.database.connection import execute_query, execute_query_with_timeout
from app.query_builder.builder import FlexibleQueryBuilder
from app.utils.errors import QueryBuildError, DatabaseError
from app.config.settings import settings

# Setup logging
logger = logging.getLogger(__name__)


class TransactionService:
    """Service for executing transaction queries."""

    @staticmethod
    async def execute_transaction_query(params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Execute a transaction query with the given parameters.

        Args:
            params: Dictionary of query parameters

        Returns:
            List of transaction records

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Build the query
            query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
            query_builder.parse_request_params(params)
            sql_query = query_builder.build_query()

            # Log the query
            logger.info(f"Executing transaction query: {sql_query}")

            # Execute with timeout if specified
            timeout = int(params.get('timeout', settings.QUERY_TIMEOUT_SECONDS))

            # Use timeout execution if timeout is specified
            if 'timeout' in params:
                results = await execute_query_with_timeout(sql_query, timeout)
            else:
                results = await execute_query(sql_query)

            # Check for empty results
            if not results:
                return []

            return results

        except QueryBuildError:
            # Re-raise query building errors
            raise
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Handle other errors
            logger.error(f"Error executing transaction query: {str(e)}", exc_info=True)
            raise QueryBuildError(f"Error executing transaction query: {str(e)}")

    @staticmethod
    async def execute_count_query(params: Dict[str, str]) -> int:
        """Execute a count query with the given parameters.

        Args:
            params: Dictionary of query parameters

        Returns:
            Count of matching records

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Build the count query
            query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
            query_builder.parse_request_params(params)
            sql_query = query_builder.build_count_query()

            # Log the query
            logger.info(f"Executing count query: {sql_query}")

            # Execute the query
            results = await execute_query(sql_query)

            # Check for empty results
            if not results or len(results) == 0:
                return 0

            # Extract count value - first row, first column
            count_result = results[0]
            count_key = next(iter(count_result))  # Get first column name
            count = count_result[count_key]

            return int(count)

        except QueryBuildError:
            # Re-raise query building errors
            raise
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Handle other errors
            logger.error(f"Error executing count query: {str(e)}", exc_info=True)
            raise QueryBuildError(f"Error executing count query: {str(e)}")

    @staticmethod
    async def get_related_companies(transaction_id: int) -> List[Dict[str, Any]]:
        """Get companies related to a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of related company information

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Build query for related companies
            params = {
                "transactionId": str(transaction_id),
                "select": "crt.transactiontocompanyreltype AS relationshipType, " +
                          "c.companyid AS companyId, " +
                          "c.companyname AS companyName, " +
                          "si.simpleindustrydescription AS industryDescription, " +
                          "geo.country AS country, " +
                          "cr.percentacquired AS percentAcquired, " +
                          "cr.currentinvestment AS investmentAmount, " +
                          "cr.leadinvestorflag AS isLeadInvestor",
                "joinRequired": "transaction_rel,company_rel,relation_type"
            }

            # Execute the query
            return await TransactionService.execute_transaction_query(params)

        except Exception as e:
            logger.error(f"Error getting related companies: {str(e)}", exc_info=True)
            raise QueryBuildError(f"Error getting related companies: {str(e)}")

    @staticmethod
    async def get_transaction_advisors(transaction_id: int) -> List[Dict[str, Any]]:
        """Get advisors for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of advisor information

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Build query for advisors
            params = {
                "transactionId": str(transaction_id),
                "select": "adv.companyid AS advisorId, " +
                          "advcompany.companyname AS advisorName, " +
                          "at.advisortypeid AS advisorTypeId, " +
                          "at.advisortypename AS advisorType",
                "joinRequired": "advisory_type,advisor_company"
            }

            # Execute the query
            return await TransactionService.execute_transaction_query(params)

        except Exception as e:
            logger.error(f"Error getting transaction advisors: {str(e)}", exc_info=True)
            raise QueryBuildError(f"Error getting transaction advisors: {str(e)}")

    @staticmethod
    async def get_transactions_by_company(company_id: int, relationship_type: Optional[str] = None) -> List[
        Dict[str, Any]]:
        """Get transactions by company.

        Args:
            company_id: Company ID
            relationship_type: Optional relationship type (buyer, seller, target)

        Returns:
            List of transaction information

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Set up basic parameters
            params = {
                "select": "tr.transactionid, tr.announcedyear, tr.announcedmonth, tr.announcedday, " +
                          "tr.transactionsize, tr.currencyid, tt.transactionidtypename"
            }

            # Add relationship type if specified
            if relationship_type:
                if relationship_type == "buyer":
                    params["buyerId"] = str(company_id)
                elif relationship_type == "seller":
                    params["sellerId"] = str(company_id)
                elif relationship_type == "target":
                    params["companyId"] = str(company_id)
                else:
                    # Default to any involvement
                    params["involvedCompanyId"] = str(company_id)
            else:
                # No relationship specified, look at direct and relationship tables
                params["involvedCompanyId"] = str(company_id)

            # Execute the query
            return await TransactionService.execute_transaction_query(params)

        except Exception as e:
            logger.error(f"Error getting transactions by company: {str(e)}", exc_info=True)
            raise QueryBuildError(f"Error getting transactions by company: {str(e)}")

    @staticmethod
    async def get_industry_statistics(industry_id: int, year: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics for an industry.

        Args:
            industry_id: Industry ID
            year: Optional year filter

        Returns:
            Dictionary of industry statistics

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        try:
            # Set up statistics parameters
            params = {
                "industry": str(industry_id),
                "select": "si.simpleindustrydescription, " +
                          "COUNT(tr.transactionid) AS transactionCount, " +
                          "SUM(tr.transactionsize) AS totalValue, " +
                          "AVG(tr.transactionsize) AS averageValue, " +
                          "MAX(tr.transactionsize) AS maxValue, " +
                          "MIN(tr.transactionsize) AS minValue",
                "groupBy": "si.simpleindustrydescription"
            }

            # Add year filter if specified
            if year:
                params["year"] = str(year)

            # Execute the query
            results = await TransactionService.execute_transaction_query(params)

            if not results or len(results) == 0:
                return {
                    "industry_id": industry_id,
                    "transaction_count": 0,
                    "total_value": 0,
                    "average_value": 0,
                    "max_value": 0,
                    "min_value": 0
                }

            # Return first result (should be only one since we're grouping by industry)
            return results[0]

        except Exception as e:
            logger.error(f"Error getting industry statistics: {str(e)}", exc_info=True)
            raise QueryBuildError(f"Error getting industry statistics: {str(e)}")

    @staticmethod
    async def validate_query(params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a query without executing it.

        Args:
            params: Query parameters to validate

        Returns:
            Dictionary with validation information

        Raises:
            QueryBuildError: If there's an error in query validation
        """
        try:
            # Try to build the query without executing it
            query_builder = FlexibleQueryBuilder(settings.SNOWFLAKE_SCHEMA)
            query_builder.parse_request_params(params)
            sql_query = query_builder.build_query()

            # Collect validation info
            validation_info = {
                "valid": True,
                "sql_query": sql_query,
                "joins": [j.get('key') for j in query_builder.joins],
                "select_fields": query_builder.select_fields,
                "where_conditions": query_builder.where_conditions,
                "group_by_fields": query_builder.group_by_fields,
                "order_by_clauses": query_builder.order_by_clauses,
                "limit": query_builder.limit_value,
                "offset": query_builder.offset_value
            }

            return validation_info

        except QueryBuildError as e:
            # Re-raise with detailed message
            raise QueryBuildError(f"Query validation failed: {str(e)}")
        except Exception as e:
            # Handle other errors
            logger.error(f"Error validating query: {str(e)}", exc_info=True)
            raise QueryBuildError(f"Error validating query: {str(e)}")