"""API routes for transaction data."""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, Path, Body, Request

from app.controllers.transaction_controller import TransactionController
from app.utils.errors import QueryBuildError, DatabaseError, SchemaCompatibilityError
from app.config.settings import settings
from app.api.dependencies import (
    get_pagination_params,
    get_api_key,
    get_schema_info,
    validate_field_mappings
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
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"}
    }
)


@router.get("/transactions")
async def get_transactions(
        # Filter parameters
        type: Optional[str] = Query(None, description="Transaction type ID"),
        year: Optional[str] = Query(None, description="Announced year"),
        month: Optional[str] = Query(None, description="Announced month"),
        day: Optional[str] = Query(None, description="Announced day"),
        country: Optional[str] = Query(None, description="Country ID"),
        industry: Optional[str] = Query(None, description="Industry ID"),
        company: Optional[str] = Query(None, description="Company ID"),
        companyName: Optional[str] = Query(None, description="Company name"),
        size: Optional[str] = Query(None, description="Transaction size"),

        # Structure parameters
        select: Optional[str] = Query(None, description="Fields to select (comma-separated)"),
        groupBy: Optional[str] = Query(None, description="Fields to group by (comma-separated)"),
        orderBy: Optional[str] = Query(None, description="Fields to order by with direction (field:asc|desc)"),
        limit: Optional[int] = Query(None, description="Maximum number of results"),
        offset: Optional[int] = Query(None, description="Number of results to skip"),

        # Pagination parameters
        page: int = Query(1, ge=1, description="Page number"),
        page_size: Optional[int] = Query(None, ge=1, le=settings.MAX_LIMIT, description="Items per page"),

        # Get all query parameters
        request: Request = Depends()
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
        # Get all query parameters including ones not explicitly listed
        params = dict(request.query_params)

        # Convert numeric parameters to strings if needed
        if limit is not None:
            params['limit'] = str(limit)
        if offset is not None:
            params['offset'] = str(offset)

        # Process request through controller with pagination
        return await TransactionController.get_transactions_with_pagination(
            params=params,
            page=page,
            page_size=page_size
        )
    except QueryBuildError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SchemaCompatibilityError as e:
        # Special handling for schema compatibility errors
        detail = f"Schema compatibility error: {str(e)}"
        if hasattr(e, 'current_hash') and hasattr(e, 'expected_hash'):
            detail += f" (Current: {e.current_hash[:8]}..., Expected: {e.expected_hash[:8]}...)"
        raise HTTPException(status_code=409, detail=detail)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/count")
async def count_transactions(
        # Filter parameters
        type: Optional[str] = Query(None, description="Transaction type ID"),
        year: Optional[str] = Query(None, description="Announced year"),
        month: Optional[str] = Query(None, description="Announced month"),
        day: Optional[str] = Query(None, description="Announced day"),
        country: Optional[str] = Query(None, description="Country ID"),
        industry: Optional[str] = Query(None, description="Industry ID"),
        company: Optional[str] = Query(None, description="Company ID"),
        companyName: Optional[str] = Query(None, description="Company name"),
        size: Optional[str] = Query(None, description="Transaction size"),

        # Get all query parameters
        request: Request = Depends()
):
    """
    Count transactions based on filter criteria without returning the actual records.

    Uses the same filtering parameters as the main transactions endpoint.
    """
    try:
        # Get all query parameters including ones not explicitly listed
        params = dict(request.query_params)

        # Get count only
        count = await TransactionController.count_transactions(params=params)
        return {"count": count}
    except QueryBuildError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{transaction_id}")
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
            raise HTTPException(status_code=404, detail=f"Transaction with ID {transaction_id} not found")

        return result
    except QueryBuildError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/analyze")
async def analyze_transactions(
        # Analysis parameters
        analysis_type: str = Query(..., description="Type of analysis to perform: trend, comparison, distribution"),
        fields: List[str] = Query(None, description="Fields to analyze"),

        # Filter parameters
        type: Optional[str] = Query(None, description="Transaction type ID"),
        year: Optional[str] = Query(None, description="Announced year"),
        month: Optional[str] = Query(None, description="Announced month"),
        day: Optional[str] = Query(None, description="Announced day"),
        country: Optional[str] = Query(None, description="Country ID"),
        industry: Optional[str] = Query(None, description="Industry ID"),

        # Get all query parameters
        request: Request = Depends()
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
        params = dict(request.query_params)

        # Get analyzed data through controller
        return await TransactionController.analyze_transactions(
            params=params,
            analysis_type=analysis_type,
            fields=fields
        )
    except QueryBuildError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/validate")
async def validate_transaction_query(
        params: Dict[str, Any] = Body(..., description="Query parameters to validate")
):
    """
    Validate transaction query parameters without executing the query.

    Returns information about the query that would be generated.
    """
    return await TransactionController.validate_transaction_query(params)


# For protected endpoints
@router.get("/transactions/protected")
async def protected_transactions(
        # Filter parameters
        type: Optional[str] = Query(None, description="Transaction type ID"),
        year: Optional[str] = Query(None, description="Announced year"),
        country: Optional[str] = Query(None, description="Country ID"),
        industry: Optional[str] = Query(None, description="Industry ID"),

        # Pagination
        page: int = Query(1, ge=1, description="Page number"),
        page_size: Optional[int] = Query(None, ge=1, le=settings.MAX_LIMIT, description="Items per page"),

        # Auth dependency
        api_key: Dict[str, Any] = Depends(get_api_key),

        # Get all query parameters
        request: Request = Depends()
):
    """
    Protected transaction endpoint that requires API key.
    """
    # Get all query parameters
    params = dict(request.query_params)

    # Apply pagination
    params["limit"] = str(page_size or settings.DEFAULT_LIMIT)
    params["offset"] = str((page - 1) * (page_size or settings.DEFAULT_LIMIT))

    # Process request through controller
    try:
        return await TransactionController.get_transactions(params)
    except QueryBuildError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Schema management related endpoints
if SCHEMA_SERVICE_AVAILABLE:
    @router.get("/schema/field-mappings")
    async def get_field_mappings(prefix: Optional[str] = None):
        """Get field mappings from schema service."""
        try:
            mappings = schema_service.field_mappings

            # Filter by prefix if provided
            if prefix:
                mappings = {k: v for k, v in mappings.items() if k.startswith(prefix)}

            return mappings
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting field mappings: {str(e)}")


    @router.get("/schema/join-paths")
    async def get_join_paths():
        """Get join paths from schema service."""
        try:
            return schema_service.join_paths
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting join paths: {str(e)}")


    @router.get("/schema/table/{table_name}")
    async def get_table_info(table_name: str):
        """Get detailed information about a table."""
        try:
            table_info = schema_service.get_table_info(table_name)
            if not table_info:
                raise HTTPException(status_code=404, detail=f"Table {table_name} not found")

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
            raise HTTPException(status_code=500, detail=f"Error getting table info: {str(e)}")