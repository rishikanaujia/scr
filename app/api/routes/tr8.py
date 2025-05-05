"""API routes for transaction queries."""
from datetime import datetime
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

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
    summary="Flexible Transaction Query Endpoint",
    description="""
    A comprehensive, flexible transaction endpoint that supports various query parameters for filtering, grouping, and sorting transaction data.

    **Common Parameter Types**:
    - **Filter fields**: Filter transactions by specific attributes like type, date components, location, industry, and company details
    - **Special operators**: Enhance filters with operators like `gte:`, `lte:`, `gt:`, `lt:`, `ne:`, `like:`, `between:`, `null:`, `notnull:`
    - **Query structure**: Control the shape and size of results with `select`, `groupBy`, `orderBy`, `limit`, `offset`
    - **Relationship filters**: Find connections between companies with `buyerId`, `sellerId`, `targetId`, `acquirerId`, `advisorId`, `advisorTypeId`
    - **Mode parameters**: Change query behavior with `count_only`, `page`, `page_size`, `include_relationships`, `include_advisors`

    **Example Use Cases**:

    1. Top Companies by Acquisition Count:
    ```
    /transactions?type=1&year=gte:2020&groupBy=companyName&select=companyName,COUNT(transactionId) AS count&orderBy=count:desc&limit=10
    ```

    2. Transaction Details with Type and Country:
    ```
    /transactions?type=14&year=2021&country=131&select=transactionId,companyName,transactionSize,transactionIdTypeName&orderBy=transactionSize:desc
    ```

    3. Transactions in Specific Industries and Country:
    ```
    /transactions?industry=32,34&country=37&year=2023&orderBy=year:desc,month:desc,day:desc
    ```

    4. Aggregate Query with Window Function:
    ```
    /transactions?type=14&year=2017&country=7,16,99&currencyId=50&select=transactionId,companyName,country,SUM(transactionSize) OVER (PARTITION BY country) AS totalValue
    ```

    5. Company Relationship Query:
    ```
    /transactions?buyerId=29096&type=2&year=gte:2022&select=transactionId,targetCompanyName,buyerCompanyName&orderBy=announcedYear:desc
    ```

    6. Count with Complex Filters:
    ```
    /transactions?type=14&industry=60&year=between:2017,2019&select=COUNT(transactionId) AS count&count_only=true
    ```

    7. Advisor Relationship Query:
    ```
    /transactions?advisorId=398625&companyId=6882342&select=COUNT(transactionId)&groupBy=companyName
    ```

    8. Cross-industry Analysis:
    ```
    /transactions?relationType=1&buyerIndustry=61,62&select=transactionId,targetCompanyName,buyerCompanyName,targetIndustryDescription
    ```
    """,
    response_description="Returns transaction data based on the specified query parameters"
)
async def query_transactions(
        request: Request,
        # Transaction type and basic filters
        type: str = Query(
            None,
            description="Transaction type ID (e.g., '1' for M&A, '2' for Acquisitions, '7' for Spin-offs, '10' for Fund Raises, '12' for Bankruptcies, '14' for Buybacks). Supports comma-separated values for multiple types.",
            example="2,14",
            openapi_extra={"nullable": True}
        ),
        # Date filters
        year: str = Query(
            None,
            description="Announced year. Supports operators: gte:, lte:, gt:, lt:, ne:, between:, and comma-separated lists",
            example="gte:2020",
            openapi_extra={"nullable": True}
        ),
        month: str = Query(
            None,
            description="Announced month (1-12). Supports operators and comma-separated lists.",
            example="1,2,3",
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
            description="Country ID. Multiple values supported with comma separator. Supports operators.",
            example="131,147",
            openapi_extra={"nullable": True}
        ),
        industry: str = Query(
            None,
            description="Industry ID. Multiple values supported with comma separator. Supports operators.",
            example="32,34",
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
            description="Transaction status ID (e.g., '2' for Completed)",
            example="2",
            openapi_extra={"nullable": True}
        ),
        # Currency related
        currencyId: str = Query(
            None,
            description="Currency ID (e.g., '50' for USD)",
            example="50",
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
            description="Relation type ID between companies (e.g., '1' for Buyer-Target)",
            example="1",
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
            description="Buyer company country ID",
            example="213",
            openapi_extra={"nullable": True}
        ),
        targetCountry: str = Query(
            None,
            description="Target company country ID",
            example="37",
            openapi_extra={"nullable": True}
        ),
        buyerIndustry: str = Query(
            None,
            description="Buyer company industry ID",
            example="56",
            openapi_extra={"nullable": True}
        ),
        targetIndustry: str = Query(
            None,
            description="Target company industry ID",
            example="61",
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
            description="Advisor type ID (e.g., '2' for Legal)",
            example="2",
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
            - Simple field selection: 'companyName,transactionSize'
            - Count: 'COUNT(transactionId) AS count'
            - Sum: 'SUM(transactionSize) AS totalValue'
            - Avg: 'AVG(transactionSize) AS averageValue'
            - Window functions: 'SUM(transactionSize) OVER (PARTITION BY country) AS totalByCountry'
            - Distinct: 'COUNT(DISTINCT simpleIndustryDescription) AS industries'""",
            example="companyName,COUNT(transactionId) AS count",
            openapi_extra={"nullable": True}
        ),
        groupBy: str = Query(
            None,
            description="Fields to group by (comma-separated). Used with aggregate functions in select.",
            example="companyName,announcedYear",
            openapi_extra={"nullable": True}
        ),
        orderBy: str = Query(
            None,
            description="Fields to order by with direction (field:asc|desc). Comma-separated for multiple fields.",
            example="transactionSize:desc,announcedYear:desc",
            openapi_extra={"nullable": True}
        ),
        limit: int = Query(
            None,
            description="Maximum number of results to return",
            example=20,
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
            # Expanded currency lookup dictionary based on common currencies
            currency_lookup = {
                "USD": "50", "EUR": "49", "GBP": "22", "JPY": "63",
                "CAD": "26", "AUD": "25", "CHF": "28", "CNY": "86",
                "HKD": "87", "SGD": "89", "INR": "92", "BRL": "93"
            }
            if iso_code in currency_lookup:
                params['currencyId'] = currency_lookup[iso_code]
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