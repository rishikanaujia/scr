"""API routes for transaction queries with name-to-ID mapping."""
from datetime import datetime
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel

from app.api.dependencies import get_api_key
from app.query_builder.controllers.transaction_controller import TransactionController
from app.utils.errors import QueryBuildError, DatabaseError
from app.config.settings import settings
from app.utils.id_name_mapper import convert_param, IDNameMapper  # Import the new mapper

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
    summary="Flexible Transaction Query Endpoint",
    description="""
    A comprehensive, flexible transaction endpoint that supports various query parameters for filtering, grouping, and sorting.

    **PARAMETER FORMATS**:
    Both numeric IDs and human-readable names are supported for parameters like type, country, industry, etc.

    Examples:
    - `type=14` or `type=Buyback` (both work)
    - `country=213` or `country=USA` (both work)
    - `industry=56` or `industry=Finance` (both work)

    **Common Parameters**:
    - **Filter fields**: Filter transactions by attributes like type, date, location, industry, etc.
    - **Special operators**: Use operators like `gte:`, `lte:`, `between:`, `null:`, `notnull:`
    - **Query structure**: Control results with `select`, `groupBy`, `orderBy`, `limit`, `offset`
    - **Relationship filters**: Connect companies with `buyerId`, `sellerId`, `targetId`, `acquirerId`

    **Example URLs**:

    1. Top Companies by Private Placement Count:
    ```
    /transactions?type=1&year=gte:2020&groupBy=companyName&select=companyName,COUNT(transactionId) as privatePlacementCount&orderBy=privatePlacementCount:desc&limit=1
    ```

    2. Transaction Details with Type and Country:
    ```
    /transactions?type=Buyback&year=2021&country=Japan&select=transactionId,companyName,transactionSize,announcedDay,announcedMonth,announcedYear,transactionIdTypeName&orderBy=transactionSize:desc&limit=1
    ```

    3. Transactions in Specific Industries and Country:
    ```
    /transactions?industry=Technology,Software&country=UK&year=2023&select=transactionId,companyName,simpleIndustryDescription,country,announcedDay,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc
    ```

    4. Buyback Count by Industry and Period:
    ```
    /transactions?type=Buyback&industry=Energy&year=between:2017,2019&select=COUNT(transactionId) as buyback_count
    ```

    5. Acquisition Count:
    ```
    /transactions?buyerId=21719&type=Acquisition&relationType=Buyer-Target&year=2018&select=COUNT(transactionId) AS acquisition_count
    ```

    **Available Values**:

    Transaction Types:
      - M&A (1)
      - Acquisition (2)
      - Spin-off (7)
      - Fund Raise (10)
      - Bankruptcy (12)
      - Buyback (14)

    Countries:
      - USA (213)
      - UK (37)
      - Japan (131)
      - Germany (147)
      - France (76)
      - Canada (102)
      - China (30)

    Industries:
      - Technology (58)
      - Software (34)
      - Finance (56)
      - Energy (60)
      - Healthcare (69)
      - Manufacturing (41)
      - Retail (23)

    Relation Types:
      - Buyer-Target (1)
      - Seller (2)

    Advisor Types:
      - Legal (2)
      - Financial (1)
    """,
    response_description="Returns transaction data based on the specified query parameters"
)
async def query_transactions(
        request: Request,
        # Transaction type and basic filters
        type: str = Query(
            None,
            description="Transaction type ID or name (e.g., '14' or 'Buyback', '2' or 'Acquisition')",
            example="Buyback",
            openapi_extra={"nullable": True}
        ),
        # Date filters
        year: str = Query(
            None,
            description="Announced year. Supports operators: gte:, lte:, gt:, lt:, ne:, between:, and comma-separated lists",
            example="2022",
            openapi_extra={"nullable": True}
        ),
        month: str = Query(
            None,
            description="Announced month (1-12). Supports operators and comma-separated lists.",
            example="3",
            openapi_extra={"nullable": True}
        ),
        day: str = Query(
            None,
            description="Announced day (1-31). Supports operators and comma-separated lists.",
            example="15",
            openapi_extra={"nullable": True}
        ),
        announcedYear: str = Query(
            None,
            description="Alternative parameter for announced year",
            example="2023",
            openapi_extra={"nullable": True}
        ),
        announcedMonth: str = Query(
            None,
            description="Alternative parameter for announced month",
            example="3",
            openapi_extra={"nullable": True}
        ),
        announcedDay: str = Query(
            None,
            description="Alternative parameter for announced day",
            example="21",
            openapi_extra={"nullable": True}
        ),
        # Location and industry filters
        country: str = Query(
            None,
            description="Country ID or name (e.g., '213' or 'USA', '37' or 'UK'). Multiple values supported with comma separator.",
            example="USA",
            openapi_extra={"nullable": True}
        ),
        industry: str = Query(
            None,
            description="Industry ID or name (e.g., '56' or 'Finance', '58' or 'Technology'). Multiple values supported with comma separator.",
            example="Finance",
            openapi_extra={"nullable": True}
        ),
        # Company identifiers
        companyId: str = Query(
            None,
            description="Company ID (for any role in transaction)",
            example="21719",
            openapi_extra={"nullable": True}
        ),
        company: str = Query(
            None,
            description="Alternative parameter for company ID",
            example="456",
            openapi_extra={"nullable": True}
        ),
        companyName: str = Query(
            None,
            description="Company name search (partial match)",
            example="Tech",
            openapi_extra={"nullable": True}
        ),
        involvedCompanyId: str = Query(
            None,
            description="Company ID that was involved in any role in the transaction",
            example="972190",
            openapi_extra={"nullable": True}
        ),
        # Transaction details
        transactionId: str = Query(
            None,
            description="Specific transaction ID for lookup",
            example="12345",
            openapi_extra={"nullable": True}
        ),
        transactionSize: str = Query(
            None,
            description="Transaction size/value. Supports operators: gte:, lte:, gt:, lt:, ne:, null:, notnull:",
            example="gte:1000000",
            openapi_extra={"nullable": True}
        ),
        size: str = Query(
            None,
            description="Alternative parameter for transaction size",
            example="gte:1000000",
            openapi_extra={"nullable": True}
        ),
        statusId: str = Query(
            None,
            description="Transaction status ID or name (e.g., '2' or 'Completed')",
            example="Completed",
            openapi_extra={"nullable": True}
        ),
        # Currency related
        currencyId: str = Query(
            None,
            description="Currency ID or name (e.g., '50' or 'USD', 'US Dollar')",
            example="USD",
            openapi_extra={"nullable": True}
        ),
        currencyIsoCode: str = Query(
            None,
            description="Currency ISO code (e.g., USD, EUR)",
            example="USD",
            openapi_extra={"nullable": True}
        ),
        currencyName: str = Query(
            None,
            description="Currency name",
            example="US Dollar",
            openapi_extra={"nullable": True}
        ),
        # Relationship identifiers
        buyerId: str = Query(
            None,
            description="Buyer company ID",
            example="29096",
            openapi_extra={"nullable": True}
        ),
        sellerId: str = Query(
            None,
            description="Seller company ID",
            example="112350",
            openapi_extra={"nullable": True}
        ),
        targetId: str = Query(
            None,
            description="Target company ID",
            example="789",
            openapi_extra={"nullable": True}
        ),
        acquirerId: str = Query(
            None,
            description="Acquirer company ID",
            example="234",
            openapi_extra={"nullable": True}
        ),
        relationType: str = Query(
            None,
            description="Relation type ID or name (e.g., '1' or 'Buyer-Target', '2' or 'Seller')",
            example="Buyer-Target",
            openapi_extra={"nullable": True}
        ),
        transactionToCompRelTypeId: str = Query(
            None,
            description="Transaction to company relationship type ID",
            example="1",
            openapi_extra={"nullable": True}
        ),
        transactionToCompanyRelType: str = Query(
            None,
            description="Transaction to company relationship type name",
            example="Buyer",
            openapi_extra={"nullable": True}
        ),
        # Related entity names
        targetCompanyName: str = Query(
            None,
            description="Target company name (for search)",
            example="Target Corp",
            openapi_extra={"nullable": True}
        ),
        buyerCompanyName: str = Query(
            None,
            description="Buyer company name (for search)",
            example="Buyer Inc",
            openapi_extra={"nullable": True}
        ),
        sellerCompanyName: str = Query(
            None,
            description="Seller company name (for search)",
            example="Seller Ltd",
            openapi_extra={"nullable": True}
        ),
        involvedCompanyName: str = Query(
            None,
            description="Name of company involved in transaction",
            example="Involved Corp",
            openapi_extra={"nullable": True}
        ),
        # Industry descriptors
        simpleIndustryDescription: str = Query(
            None,
            description="Simple industry description (for search)",
            example="Technology",
            openapi_extra={"nullable": True}
        ),
        targetIndustryDescription: str = Query(
            None,
            description="Target company industry description",
            example="Software",
            openapi_extra={"nullable": True}
        ),
        buyerIndustryDescription: str = Query(
            None,
            description="Buyer company industry description",
            example="Hardware",
            openapi_extra={"nullable": True}
        ),
        # Transaction type name
        transactionIdTypeName: str = Query(
            None,
            description="Transaction type name",
            example="Acquisition",
            openapi_extra={"nullable": True}
        ),
        # Cross filters (by country or industry for related entities)
        buyerCountry: str = Query(
            None,
            description="Buyer company country ID or name (e.g., '213' or 'USA')",
            example="USA",
            openapi_extra={"nullable": True}
        ),
        targetCountry: str = Query(
            None,
            description="Target company country ID or name (e.g., '37' or 'UK')",
            example="UK",
            openapi_extra={"nullable": True}
        ),
        buyerIndustry: str = Query(
            None,
            description="Buyer company industry ID or name (e.g., '56' or 'Finance')",
            example="Finance",
            openapi_extra={"nullable": True}
        ),
        targetIndustry: str = Query(
            None,
            description="Target company industry ID or name (e.g., '61' or 'Internet')",
            example="Internet",
            openapi_extra={"nullable": True}
        ),
        # Advisor related
        advisorId: str = Query(
            None,
            description="Advisor company ID",
            example="398625",
            openapi_extra={"nullable": True}
        ),
        advisorTypeId: str = Query(
            None,
            description="Advisor type ID or name (e.g., '2' or 'Legal')",
            example="Legal",
            openapi_extra={"nullable": True}
        ),
        advisorCompanyName: str = Query(
            None,
            description="Advisor company name (for search)",
            example="Legal Advisors Inc",
            openapi_extra={"nullable": True}
        ),
        # Query structure parameters
        select: str = Query(
            None,
            description="""Fields to select (comma-separated). Supports SQL-like functions:
            - Simple fields: 'companyName,transactionSize'
            - Count: 'COUNT(transactionId) AS count' or 'COUNT(transactionId) as dealCount'
            - Sum: 'SUM(transactionSize) AS totalValue' or 'SUM(transactionSize) as totalTransactionValue'
            - Avg: 'AVG(transactionSize)' or 'AVG(transactionsize)'
            - Distinct: 'COUNT(DISTINCT simpleIndustryDescription) as industries_with_buybacks'
            - Window functions: 'SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue'""",
            example="companyName,COUNT(transactionId) AS count",
            openapi_extra={"nullable": True}
        ),
        groupBy: str = Query(
            None,
            description="Fields to group by (comma-separated). Used with aggregate functions in select.",
            example="companyName",
            openapi_extra={"nullable": True}
        ),
        orderBy: str = Query(
            None,
            description="Fields to order by with direction (field:asc|desc). Comma-separated for multiple fields.",
            example="transactionSize:desc",
            openapi_extra={"nullable": True}
        ),
        limit: int = Query(
            None,
            description="Maximum number of results to return",
            example=10,
            ge=1,
            openapi_extra={"nullable": True}
        ),
        offset: int = Query(
            None,
            description="Number of results to skip (for pagination)",
            example=0,
            ge=0,
            openapi_extra={"nullable": True}
        ),
        # Special operation mode parameters
        count_only: bool = Query(
            False,
            description="Return only the count of matching transactions. Useful with COUNT() aggregations.",
            example=False
        ),
        page: int = Query(
            None,
            description="Page number for pagination. Used with page_size.",
            example=1,
            ge=1,
            openapi_extra={"nullable": True}
        ),
        page_size: int = Query(
            None,
            description="Number of items per page for pagination. Used with page.",
            example=10,
            ge=1,
            openapi_extra={"nullable": True}
        ),
        include_relationships: bool = Query(
            False,
            description="Include related company relationships in the response",
            example=False
        ),
        include_advisors: bool = Query(
            False,
            description="Include transaction advisors in the response",
            example=False
        ),
        includeAdvisors: str = Query(
            None,
            description="Alternative parameter to include advisors ('true'/'false')",
            example="true",
            openapi_extra={"nullable": True}
        ),
        # Analysis parameters
        analysisType: str = Query(
            None,
            description="Type of analysis to perform (e.g., 'trend', 'comparison')",
            example="trend",
            openapi_extra={"nullable": True}
        ),
        fields: str = Query(
            None,
            description="Fields to include in analysis (comma-separated)",
            example="year,month,size",
            openapi_extra={"nullable": True}
        ),
        api_key: Dict = Depends(get_api_key)
):
    try:
        # Build parameters dictionary from provided values
        params = {}

        # Get all local variables except these excluded ones
        exclude_keys = ['request', 'api_key', 'params']

        # Add explicitly defined parameters that were provided (not None)
        for key, value in locals().items():
            if key not in exclude_keys and value is not None:
                # If it's a string value, check if it needs name-to-ID conversion
                if isinstance(value, str):
                    # Convert names to IDs for specific parameters
                    if key in ['type', 'country', 'industry', 'statusId', 'currencyId',
                               'relationType', 'buyerCountry', 'targetCountry',
                               'buyerIndustry', 'targetIndustry', 'advisorTypeId']:
                        params[key] = convert_param(key, value)
                    else:
                        params[key] = value
                else:
                    params[key] = value

        # Handle parameter aliases and transformations

        # Handle company parameter alias
        if 'company' in params and 'companyId' not in params:
            params['companyId'] = params.pop('company')

        # Handle size parameter alias
        if 'size' in params and 'transactionSize' not in params:
            params['transactionSize'] = params.pop('size')

        # Handle includeAdvisors string to boolean conversion
        if 'includeAdvisors' in params:
            include_advisors_str = params.pop('includeAdvisors')
            if include_advisors_str.lower() == 'true' and not params.get('include_advisors', False):
                params['include_advisors'] = True

        # Handle announced date components from year/month/day if not using announcedYear/Month/Day
        if 'year' in params and 'announcedYear' not in params:
            params['announcedYear'] = params.get('year')

        if 'month' in params and 'announcedMonth' not in params:
            params['announcedMonth'] = params.get('month')

        if 'day' in params and 'announcedDay' not in params:
            params['announcedDay'] = params.get('day')

        # Handle special operation modes
        # -----------------------------

        # Check if it's a single transaction lookup by ID
        transaction_id = params.pop('transactionId', None)
        if transaction_id:
            # Get include flags
            include_relationships = params.pop('include_relationships', False)
            include_advisors = params.pop('include_advisors', False)

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
        count_only = params.pop('count_only', False)
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
                    "page": str(page),
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

        # Handle currency ISO code
        if 'currencyIsoCode' in params:
            # This would need to be translated to currencyId
            iso_code = params.pop('currencyIsoCode')
            # Use mapper to convert ISO code to ID
            currency_id = IDNameMapper.get_currency_id(iso_code)
            if currency_id:
                params['currencyId'] = str(currency_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown currency ISO code: {iso_code}"
                )

        # Handle analytics parameters
        # --------------------------

        # Check for analysis type
        analysis_type = params.pop('analysisType', None)
        fields_str = params.pop('fields', None)
        if analysis_type:
            fields_list = [f.strip() for f in fields_str.split(',')] if fields_str else None

            # Execute analysis
            result = await TransactionController.analyze_transactions(params, analysis_type, fields_list)

            return {
                "data": result,
                "query_parameters": {
                    **params,
                    "analysisType": analysis_type,
                    "fields": fields_str or ""
                },
                "timestamp": datetime.now().isoformat()
            }

        # Check for advisor relationships
        advisor_id = params.get('advisorId', None)
        advisor_type = params.get('advisorTypeId', None)
        if advisor_id or advisor_type or 'advisorCompanyName' in params:
            # Set flag to include advisor information
            params['include_advisors'] = True

        # Handle entity specific queries
        if ('buyerCountry' in params or 'buyerIndustry' in params or
                'targetCountry' in params or 'targetIndustry' in params):
            # These fields indicate cross-entity filtering
            params['include_relationships'] = True

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