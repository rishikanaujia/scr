"""API routes for transaction data."""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, Path, Body, Request, status

from app.controllers.transaction_controller import TransactionController
from app.utils.errors import QueryBuildError, DatabaseError, SchemaCompatibilityError
from app.config.settings import settings
from app.api.dependencies import (
    get_api_key,
    get_schema_info,
    validate_field_mappings
)
from app.models import (
    TransactionQueryParams,
    PaginationParams,
    AnalysisParams,
    TransactionListResponse,
    TransactionDetailResponse,
    AnalysisResponse,
    ErrorResponse
)

# Try to import schema management components
try:
    from app.schema_management import schema_service

    SCHEMA_SERVICE_AVAILABLE = True
except ImportError:
    SCHEMA_SERVICE_AVAILABLE = False

# Create router
router = APIRouter(
    prefix=f"{settings.API_PREFIX}",
    tags=["transactions"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


# Helper function to extract all query parameters
def get_all_query_params(request: Request) -> Dict[str, Any]:
    """Extract all query parameters from the request."""
    return dict(request.query_params)


@router.get(
    "/transactions",
    response_model=TransactionListResponse,
    responses={
        status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Schema Compatibility Error"}
    }
)
async def get_transactions(
        request: Request,
        query_params: TransactionQueryParams = Depends(),
        pagination: PaginationParams = Depends(),
):
    """
    Flexible transaction endpoint that supports various query parameters:
    - Filter fields: type, year, month, day, country, industry, company, size
    - Special operators: gte:, lte:, gt:, lt:, ne:, comma for IN
    - Query structure: select, groupBy, orderBy, limit, offset

    Examples:
    - /api/v1/transactions?type=1&year=gte:2020&groupBy=companyName&orderBy=count:desc&limit=10
    - /api/v1/transactions?type=14&year=2021&country=131&orderBy=size:desc&limit=20
    - /api/v1/transactions?industry=32,34&country=37&year=2023&orderBy=year:desc,month:desc,day:desc
    """
    try:
        # Get all query parameters
        params = get_all_query_params(request)

        # Process request through controller with pagination
        return await TransactionController.get_transactions_with_pagination(
            params=params,
            page=pagination.page,
            page_size=pagination.page_size
        )
    except QueryBuildError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SchemaCompatibilityError as e:
        # Special handling for schema compatibility errors
        detail = f"Schema compatibility error: {str(e)}"
        if hasattr(e, 'current_hash') and hasattr(e, 'expected_hash'):
            detail += f" (Current: {e.current_hash[:8]}..., Expected: {e.expected_hash[:8]}...)"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/transactions/count",
    response_model=Dict[str, int]
)
async def count_transactions(
        request: Request,
        query_params: TransactionQueryParams = Depends(),
):
    """
    Count transactions based on filter criteria without returning the actual records.

    Uses the same filtering parameters as the main transactions endpoint.
    """
    try:
        # Get all query parameters
        params = get_all_query_params(request)

        # Get count only
        count = await TransactionController.count_transactions(params=params)
        return {"count": count}
    except QueryBuildError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionDetailResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Transaction not found"}
    }
)
async def get_transaction_by_id(
        transaction_id: int = Path(..., title="Transaction ID", description="Unique identifier for a transaction"),
        include_companies: bool = Query(False, description="Include related companies"),
        include_advisors: bool = Query(False, description="Include transaction advisors")
):
    """
    Get a specific transaction by its ID.

    Optional parameters:
    - include_companies: Whether to include related companies (target, acquirer, etc.)
    - include_advisors: Whether to include transaction advisors
    """
    try:
        # If including related data, use the enriched method
        if include_companies or include_advisors:
            result = await TransactionController.get_transaction_with_related(
                transaction_id,
                include_companies=include_companies,
                include_advisors=include_advisors
            )
        else:
            # Simple lookup for just the transaction
            result = await TransactionController.get_transaction_by_id(transaction_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found"
            )

        return result
    except QueryBuildError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/transactions/analyze",
    response_model=AnalysisResponse
)
async def analyze_transactions(
        request: Request,
        analysis: AnalysisParams = Depends(),
        query_params: TransactionQueryParams = Depends(),
):
    """
    Analyze transaction data based on specified parameters.

    Analysis types:
    - trend: Analyze trends over time
    - comparison: Compare values across categories
    - distribution: Analyze distribution of values
    """
    try:
        # Get all query parameters
        params = get_all_query_params(request)

        # Get analyzed data through controller
        return await TransactionController.analyze_transactions(
            params=params,
            analysis_type=analysis.analysis_type,
            fields=analysis.fields
        )
    except QueryBuildError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/transactions/validate",
    response_model=Dict[str, Any]
)
async def validate_transaction_query(
        params: Dict[str, Any] = Body(..., description="Query parameters to validate")
):
    """
    Validate transaction query parameters without executing the query.

    Returns information about the query that would be generated.
    """
    return await TransactionController.validate_transaction_query(params)


@router.get(
    "/transactions/protected",
    response_model=TransactionListResponse
)
async def protected_transactions(
        request: Request,
        api_key: Dict[str, Any] = Depends(get_api_key),
        pagination: PaginationParams = Depends(),
        query_params: TransactionQueryParams = Depends(),
):
    """
    Protected transaction endpoint that requires API key.
    """
    # Get all query parameters
    params = get_all_query_params(request)

    # Apply pagination
    params["limit"] = str(pagination.page_size or settings.DEFAULT_LIMIT)
    params["offset"] = str((pagination.page - 1) * (pagination.page_size or settings.DEFAULT_LIMIT))

    # Process request through controller
    try:
        return await TransactionController.get_transactions(params)
    except QueryBuildError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Schema management related endpoints
if SCHEMA_SERVICE_AVAILABLE:
    @router.get(
        "/schema/field-mappings",
        response_model=Dict[str, Any]
    )
    async def get_field_mappings(
            prefix: Optional[str] = None
    ):
        """Get field mappings from schema service."""
        try:
            mappings = schema_service.field_mappings

            # Filter by prefix if provided
            if prefix:
                mappings = {k: v for k, v in mappings.items() if k.startswith(prefix)}

            return mappings
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting field mappings: {str(e)}"
            )


    @router.get(
        "/schema/join-paths",
        response_model=Dict[str, Any]
    )
    async def get_join_paths():
        """Get join paths from schema service."""
        try:
            return schema_service.join_paths
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting join paths: {str(e)}"
            )


    @router.get(
        "/schema/table/{table_name}",
        response_model=Dict[str, Any],
        responses={
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Table not found"}
        }
    )
    async def get_table_info(table_name: str):
        """Get detailed information about a table."""
        try:
            table_info = schema_service.get_table_info(table_name)
            if not table_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table {table_name} not found"
                )

            # Convert to serializable format
            serializable = {
                "name": table_info.name,
                "alias": table_info.alias,
                "columns": [],
                "primary_keys": table_info.primary_keys,
                "joins": []
            }

            # Add columns
            for name, col in table_info.columns.items():
                serializable["columns"].append({
                    "name": name,
                    "field_id": col.field_id,
                    "data_type": col.data_type,
                    "nullable": col.nullable,
                    "is_primary": col.is_primary
                })

            # Add joins
            for key, join in table_info.joins.items():
                serializable["joins"].append({
                    "key": key,
                    "target_table": join.target_table,
                    "target_alias": join.target_alias,
                    "join_type": join.join_type,
                    "requires": list(join.requires)
                })

            return serializable
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting table info: {str(e)}"
            )