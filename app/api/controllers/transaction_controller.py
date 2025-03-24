"""Transaction controller for managing application logic."""
import logging
from typing import Dict, List, Any, Optional

from app.services.transaction_service import TransactionService
from app.utils.errors import QueryBuildError, DatabaseError, SchemaCompatibilityError
from app.config.settings import settings

# Try to import schema management components
try:
    from app.schema_management import schema_service
    from app.utils.schema_adapter import SchemaAdapter

    SCHEMA_SERVICE_AVAILABLE = True
except ImportError:
    SCHEMA_SERVICE_AVAILABLE = False

# Setup logging
logger = logging.getLogger(__name__)


class TransactionController:
    """Controller for transaction-related operations."""

    @staticmethod
    async def get_transactions(params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Get transactions based on parameters.

        Args:
            params: Dictionary of query parameters

        Returns:
            List of transaction records

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        return await TransactionService.execute_transaction_query(params)

    @staticmethod
    async def count_transactions(params: Dict[str, str]) -> int:
        """Count transactions based on parameters.

        Args:
            params: Dictionary of query parameters

        Returns:
            Number of matching transactions

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        return await TransactionService.execute_count_query(params)

    @staticmethod
    async def get_transactions_with_pagination(
            params: Dict[str, str],
            page: int = 1,
            page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get transactions with pagination.

        Args:
            params: Dictionary of query parameters
            page: Page number (1-based)
            page_size: Number of records per page (defaults to settings.DEFAULT_LIMIT)

        Returns:
            Dictionary with pagination info and transaction records

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        # Set default page size if not provided
        if page_size is None:
            page_size = settings.DEFAULT_LIMIT

        # Ensure page is at least 1
        if page < 1:
            page = 1

        # Apply pagination parameters
        pagination_params = params.copy()
        pagination_params['limit'] = str(page_size)
        pagination_params['offset'] = str((page - 1) * page_size)

        try:
            # Get total count (without pagination)
            total_count = await TransactionController.count_transactions(params)

            # Get paginated results
            results = await TransactionController.get_transactions(pagination_params)

            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
            has_next = page < total_pages
            has_prev = page > 1

            return {
                'data': results,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            }
        except (QueryBuildError, DatabaseError):
            # Re-raise specific errors
            raise
        except Exception as e:
            # Handle other errors
            logger.error(f"Error in paginated transaction service: {str(e)}", exc_info=True)
            raise DatabaseError(f"Error processing paginated transaction request: {str(e)}")

    @staticmethod
    async def get_transaction_by_id(transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction record or None if not found

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        # Query for a specific transaction ID
        params = {"transactionId": str(transaction_id)}
        results = await TransactionController.get_transactions(params)

        if not results or len(results) == 0:
            return None

        return results[0]

    @staticmethod
    async def get_transaction_with_related(
            transaction_id: int,
            include_companies: bool = True,
            include_advisors: bool = False
    ) -> Dict[str, Any]:
        """Get a transaction with related entities.

        Args:
            transaction_id: Transaction ID
            include_companies: Whether to include related companies
            include_advisors: Whether to include advisors

        Returns:
            Transaction with related entities

        Raises:
            QueryBuildError: If there's an error building the query
            DatabaseError: If there's an error executing the query
        """
        # Get the base transaction
        params = {"transactionId": str(transaction_id)}

        # Add SELECT fields
        select_fields = ["tr.*", "tt.transactionidtypename AS typeName"]

        # Include related companies if requested
        if include_companies:
            select_fields.extend([
                "c.companyname AS companyName",
                "si.simpleindustrydescription AS industryDescription",
                "geo.country AS countryName"
            ])

        # Include advisors if requested
        if include_advisors:
            select_fields.extend([
                "advcompany.companyname AS advisorName",
                "at.advisortypename AS advisoryRole"
            ])

        # Create SELECT parameter
        params["select"] = ",".join(select_fields)

        # Execute query
        results = await TransactionController.get_transactions(params)

        if not results or len(results) == 0:
            return {}

        # Get the main transaction record
        transaction = results[0]

        # If companies are included, get related companies (target, acquirer, etc.)
        if include_companies:
            transaction['relatedCompanies'] = await TransactionService.get_related_companies(transaction_id)

        # If advisors are included, get advisors
        if include_advisors:
            transaction['advisors'] = await TransactionService.get_transaction_advisors(transaction_id)

        return transaction

    @staticmethod
    async def analyze_transactions(
            params: Dict[str, str],
            analysis_type: str,
            fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze transaction data.

        Args:
            params: Dictionary of query parameters
            analysis_type: Type of analysis (trend, comparison, distribution)
            fields: Fields to analyze

        Returns:
            Analyzed transaction data
        """
        # Create a copy of params to modify
        request = params.copy()

        # Map fields if provided
        mapped_fields = []
        if fields:
            for field in fields:
                if SCHEMA_SERVICE_AVAILABLE:
                    mapped_field = SchemaAdapter.get_field_mapping(field)
                    mapped_fields.append(mapped_field)
                else:
                    mapped_fields.append(field)

        # Basic implementation - can be expanded with more advanced analytics
        if analysis_type == "trend":
            # Add time-based grouping if not already present
            if "groupBy" not in request:
                request["groupBy"] = "year,month"
            if "select" not in request:
                request["select"] = "year,month,count"

        elif analysis_type == "comparison":
            # For comparison, ensure we have category and measure
            if "groupBy" not in request and mapped_fields and len(mapped_fields) > 0:
                request["groupBy"] = mapped_fields[0]
            if "select" not in request:
                request["select"] = "count"

        elif analysis_type == "distribution":
            # For distribution, we need to bin values
            if "select" not in request and mapped_fields and len(mapped_fields) > 0:
                request["select"] = mapped_fields[0]

        # Get analyzed data
        return await TransactionService.execute_transaction_query(request)

    @staticmethod
    async def validate_transaction_query(params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transaction query parameters.

        Args:
            params: Query parameters to validate

        Returns:
            Validation information
        """
        validation_info = await TransactionService.validate_query(params)

        # Add schema info if available
        if SCHEMA_SERVICE_AVAILABLE:
            try:
                schema_info = {
                    "tables_count": len(schema_service.tables) if hasattr(schema_service, "tables") else 0,
                    "adapter_mode": getattr(settings, "SCHEMA_ADAPTER_MODE", "static"),
                }
                validation_info["schema_info"] = schema_info
            except Exception as e:
                logger.warning(f"Error getting schema info: {str(e)}")

        return validation_info