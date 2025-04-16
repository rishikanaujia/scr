"""API routes for transaction queries."""
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel

from app.api.dependencies import get_api_key
from app.query_builder.controllers.transaction_controller import TransactionController
from app.utils.errors import QueryBuildError, DatabaseError
from app.config.settings import settings

# Define API prefix from settings
API_PREFIX = settings.API_PREFIX


# Define response models
class TransactionResponse(BaseModel):
    data: List[Dict[str, Any]]  # Using Dict for flexibility
    query_parameters: Dict[str, str]
    timestamp: str


# Create router
router = APIRouter(
    prefix=f"{API_PREFIX}",
    tags=["transactions"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"}
    }
)


@router.get(
    "/transactions",
    response_model=TransactionResponse,
    summary="Flexible Transaction Query",
    description="""
    Flexible transaction endpoint that supports various query parameters for filtering, grouping, and sorting.

    Common Parameters:
    - Filter fields: type, year, month, day, country, industry, companyId, size
    - Special operators: gte:, lte:, gt:, lt:, ne:, like:, between:, null:, notnull:
    - Query structure: select, groupBy, orderBy, limit, offset
    - Relationship filters: buyerId, sellerId, targetId, acquirerId, advisorId, advisorTypeId
    - Mode parameters: count_only, page, page_size, include_relationships, include_advisors

    Examples:
    - Top companies by acquisition count:
      ?type=1&year=gte:2020&groupBy=companyName&select=companyName,COUNT(transactionId) AS count&orderBy=count:desc&limit=10

    - Transactions in specific industries and country:
      ?industry=32,34&country=37&year=2023&orderBy=year:desc,month:desc,day:desc

    - Aggregate query with window function:
      ?type=14&year=2017&country=7,16,99&currencyId=50&select=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue

    - Company relationship query:
      ?buyerId=29096&type=2&year=gte:2022&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName

    - Count with complex filters:
      ?type=14&industry=60&year=between:2017,2019&select=COUNT(transactionId) AS count&count_only=true
    """
)
async def query_transactions(
        request: Request,
        api_key: Dict = Depends(get_api_key)
):
    try:
        # Get all query parameters from request
        params = dict(request.query_params)

        # Handle special operation modes
        # -----------------------------

        # Check if it's a single transaction lookup by ID
        transaction_id = params.pop('transactionId', None)
        if transaction_id:
            # Get include flags
            include_relationships = params.pop('include_relationships', 'false').lower() == 'true'
            include_advisors = params.pop('include_advisors', 'false').lower() == 'true'

            transaction = await TransactionController.get_transaction_with_related(
                int(transaction_id),
                include_relationships,
                include_advisors
            )

            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Transaction {transaction_id} not found"
                )

            return {
                "data": [transaction],
                "query_parameters": {"transactionId": transaction_id, **params},
                "timestamp": datetime.now().isoformat()
            }

        # Check if count-only mode is requested
        count_only = params.pop('count_only', 'false').lower() == 'true'
        if count_only:
            count = await TransactionController.count_transactions(params)
            return {
                "data": [{"count": count}],
                "query_parameters": params,
                "timestamp": datetime.now().isoformat()
            }

        # Check if pagination is requested
        page = params.pop('page', None)
        page_size = params.pop('page_size', None)
        if page is not None:
            try:
                page_num = int(page)
                page_size_num = int(page_size) if page_size else settings.DEFAULT_LIMIT
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid page or page_size parameter"
                )

            result = await TransactionController.get_transactions_with_pagination(
                params,
                page_num,
                page_size_num
            )

            return {
                "data": result['data'],
                "query_parameters": {
                    **params,
                    "page": page,
                    "page_size": str(page_size_num),
                    "total_count": str(result['pagination']['total_count']),
                    "total_pages": str(result['pagination']['total_pages'])
                },
                "timestamp": datetime.now().isoformat()
            }

        # Handle special relationship parameters
        # --------------------------------------

        # Handle relationship types (convert to appropriate join parameters)
        if 'relationType' in params:
            relation_type = params.pop('relationType')
            # Add the appropriate parameter for the filter parser
            params['transactionToCompRelTypeId'] = relation_type

        # Handle buyer country/industry filters
        if 'buyerCountry' in params or 'buyerIndustry' in params:
            # These require special handling in join analyzer
            # Pass them through as is - the filter parser will handle them
            pass

        # Handle target country/industry filters
        if 'targetCountry' in params or 'targetIndustry' in params:
            # These require special handling in join analyzer
            # Pass them through as is - the filter parser will handle them
            pass

        # Handle currency ISO code
        if 'currencyIsoCode' in params:
            # This would need to be translated to currencyId
            # In a real implementation, this might query a currency lookup table
            iso_code = params.pop('currencyIsoCode')
            # Simulate lookup (in real code, this would query the database)
            currency_lookup = {"USD": "50"}
            if iso_code in currency_lookup:
                params['currencyId'] = currency_lookup[iso_code]

        # Handle analytics parameters
        # --------------------------

        # Check for analysis type
        analysis_type = params.pop('analysisType', None)
        if analysis_type:
            fields_str = params.pop('fields', '')
            fields_list = [f.strip() for f in fields_str.split(',')] if fields_str else None

            # Execute analysis
            result = await TransactionController.analyze_transactions(params, analysis_type, fields_list)

            return {
                "data": result,
                "query_parameters": {
                    **params,
                    "analysisType": analysis_type,
                    "fields": fields_str
                },
                "timestamp": datetime.now().isoformat()
            }

        # Check for advisor relationships
        advisor_id = params.get('advisorId', None)
        advisor_type = params.get('advisorTypeId', None)
        if advisor_id or advisor_type:
            # Set flag to include advisor information
            params['includeAdvisors'] = 'true'

        # Standard query execution
        # -----------------------
        result = await TransactionController.get_transactions(params)

        return {
            "data": result,
            "query_parameters": params,
            "timestamp": datetime.now().isoformat()
        }

    except QueryBuildError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get Transaction by ID",
    description="Get a single transaction by its ID with optional related entities"
)
async def get_transaction_by_id(
        transaction_id: int,
        include_relationships: bool = Query(False, description="Include related company relationships"),
        include_advisors: bool = Query(False, description="Include transaction advisors"),
        api_key: Dict = Depends(get_api_key)
):
    try:
        transaction = await TransactionController.get_transaction_with_related(
            transaction_id,
            include_relationships,
            include_advisors
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {transaction_id} not found"
            )

        return {
            "data": [transaction],
            "query_parameters": {
                "transactionId": str(transaction_id),
                "include_relationships": str(include_relationships),
                "include_advisors": str(include_advisors)
            },
            "timestamp": datetime.now().isoformat()
        }
    except QueryBuildError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/transactions/count",
    response_model=TransactionResponse,
    summary="Count Transactions",
    description="Count transactions matching the filter criteria"
)
async def count_transactions(
        request: Request,
        api_key: Dict = Depends(get_api_key)
):
    try:
        # Get all query parameters from request
        params = dict(request.query_params)

        # Get count
        count = await TransactionController.count_transactions(params)

        return {
            "data": [{"count": count}],
            "query_parameters": params,
            "timestamp": datetime.now().isoformat()
        }
    except QueryBuildError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))