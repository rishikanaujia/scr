"""API routes for transaction queries with name-to-ID mapping."""
from datetime import datetime
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel

from app.api.dependencies import get_api_key
from app.query_builder.controllers.transaction_controller import TransactionController
from app.utils.errors import QueryBuildError, DatabaseError
from app.config.settings import settings

# Import the ID-Name mapper and examples
from app.utils.id_name_mapper import convert_param, IDNameMapper
from app.utils.transaction_examples import (
    get_transaction_examples,
    get_example_openapi_extensions,
    get_reference_values
)

# Define API prefix from settings
API_PREFIX = settings.API_PREFIX


# Define response models
class TransactionResponse(BaseModel):
    data: List[Dict[str, Any]]  # Using Dict for flexibility
    query_parameters: Dict[str, str]
    timestamp: str


class ExampleQuery(BaseModel):
    name: str
    url: str
    url_with_names: str
    description: str


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
    "/transactions/examples",
    response_model=List[ExampleQuery],
    summary="Transaction API Example Queries",
    description="Returns a comprehensive list of example transaction API queries with descriptions.",
    tags=["documentation"]
)
async def transaction_examples():
    """
    Provides a list of example queries for the Transaction API.

    Each example includes:
    - A descriptive name
    - The URL using numeric IDs
    - An equivalent URL using human-readable names
    - A description of what the query does

    This endpoint is designed to help users and LLMs understand how to use the API effectively.
    """
    return get_transaction_examples()


@router.get(
    "/transactions/reference",
    summary="Transaction API Reference Values",
    description="Returns reference values for all entity types (transaction types, countries, industries, etc.)",
    tags=["documentation"]
)
async def transaction_reference_values():
    """
    Provides reference values for all entity types used in the Transaction API.

    Includes mappings between IDs and names for:
    - Transaction types (1=M&A, 2=Acquisition, 14=Buyback, etc.)
    - Countries (213=USA, 37=UK, etc.)
    - Industries (56=Finance, 69=Healthcare, etc.)
    - Currencies, statuses, advisor types, and relation types

    This endpoint is useful for understanding the available values and their mappings.
    """
    return get_reference_values()


@router.get(
    "/openapi-llm.json",
    summary="Enhanced OpenAPI Schema for LLMs",
    description="Returns an enhanced OpenAPI schema with detailed examples specifically designed for LLMs.",
    tags=["documentation"],
    include_in_schema=False
)
async def get_openapi_llm(request: Request):
    """
    Returns a specialized OpenAPI schema with enhancements for LLMs.

    This schema includes:
    - Comprehensive example queries
    - Mappings between IDs and names for all entity types
    - Enhanced parameter descriptions

    This endpoint is designed to make it easier for LLMs to generate correct API calls.
    """
    # Get the base OpenAPI schema
    from fastapi.openapi.utils import get_openapi

    app = request.app
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Enhance the schema with examples and mappings
    openapi_schema.update(get_example_openapi_extensions())

    return openapi_schema


@router.get(
    "/transactions",
    response_model=TransactionResponse,
    summary="Flexible Transaction Query Endpoint",
    description="""
    # Transaction API - Flexible Query Endpoint

    A comprehensive transaction endpoint supporting various query parameters for filtering, grouping, and sorting.

    ## Parameter Format
    Both numeric IDs and human-readable names are supported for parameters like type, country, industry, etc.

    Examples:
    - `type=14` or `type=Buyback` (both work)
    - `country=213` or `country=USA` (both work)
    - `industry=56` or `industry=Finance` (both work)

    ## Common Query Patterns

    ### Basic Filtering
    ```
    /transactions?type=14&year=2022&country=213
    /transactions?type=Buyback&year=2022&country=USA
    ```

    ### Aggregation Functions
    ```
    /transactions?type=14&year=2022&select=COUNT(transactionId) as count
    /transactions?type=Buyback&industry=Finance&select=SUM(transactionSize) as total
    ```

    ### Grouping and Ordering
    ```
    /transactions?year=2022&groupBy=industry&select=industry,COUNT(transactionId) as count
    /transactions?year=2022&orderBy=transactionSize:desc&limit=10
    ```

    ### Advanced Operators
    ```
    /transactions?year=gte:2020&transactionSize=notnull:
    /transactions?year=between:2018,2021&country=ne:213
    ```

    ## Reference Values

    ### Transaction Types
    - 1: M&A
    - 2: Acquisition
    - 7: Spin-off
    - 10: Fund Raise
    - 12: Bankruptcy
    - 14: Buyback

    ### Common Countries
    - 213: USA
    - 37: UK
    - 131: Japan
    - 147: Germany
    - 76: France

    ### Common Industries
    - 32: Technology Hardware
    - 34: Software
    - 56: Finance
    - 60: Energy
    - 69: Healthcare

    See the `/transactions/examples` endpoint for a complete set of example queries.
    """,
    response_description="Returns transaction data based on the specified query parameters",
    openapi_extra={
        "x-examples": {
            "top_companies": {
                "summary": "Top Companies by Private Placement Count",
                "value": {
                    "query": "type=1&year=gte:2020&groupBy=companyName&select=companyName,COUNT(transactionId) as privatePlacementCount&orderBy=privatePlacementCount:desc&limit=1"}
            },
            "buybacks": {
                "summary": "Buyback Transactions",
                "value": {
                    "query": "type=14&year=2022&country=213&select=transactionId,companyName,transactionSize&orderBy=transactionSize:desc"}
            },
            "acquisitions_with_name": {
                "summary": "Acquisitions Using Name Instead of ID",
                "value": {
                    "query": "type=Acquisition&year=2022&country=USA&select=transactionId,companyName,transactionSize&orderBy=transactionSize:desc"}
            }
        }
    }
)
async def query_transactions(
        request: Request,
        # Transaction type and basic filters
        type: str = Query(
            None,
            description="""Transaction type ID or name. Examples:
            - Use IDs: '1', '2', '14'  
            - Or names: 'M&A', 'Acquisition', 'Buyback'

            Reference values:
            - 1: M&A
            - 2: Acquisition 
            - 7: Spin-off
            - 10: Fund Raise
            - 12: Bankruptcy
            - 14: Buyback""",
            example="14",
            openapi_extra={"nullable": True}
        ),
        # Date filters
        year: str = Query(
            None,
            description="Announced year. Supports operators: gte:, lte:, gt:, lt:, ne:, between:, and comma-separated lists. Examples: '2022', 'gte:2020', 'between:2018,2021'.",
            example="2022",
            openapi_extra={"nullable": True}
        ),
        month: str = Query(
            None,
            description="Announced month (1-12). Supports operators and comma-separated lists. Examples: '3' for March, '1,2,3' for Q1.",
            example="3",
            openapi_extra={"nullable": True}
        ),
        day: str = Query(
            None,
            description="Announced day (1-31). Supports operators and comma-separated lists. Examples: '15', 'gte:20'.",
            example="15",
            openapi_extra={"nullable": True}
        ),
        announcedYear: str = Query(
            None,
            description="Alternative parameter for announced year. Examples: '2023', 'gte:2020'.",
            example="2023",
            openapi_extra={"nullable": True}
        ),
        announcedMonth: str = Query(
            None,
            description="Alternative parameter for announced month. Examples: '3' for March.",
            example="3",
            openapi_extra={"nullable": True}
        ),
        announcedDay: str = Query(
            None,
            description="Alternative parameter for announced day. Examples: '21'.",
            example="21",
            openapi_extra={"nullable": True}
        ),
        # Location and industry filters
        country: str = Query(
            None,
            description="""Country ID or name. Examples:
            - Use IDs: '213', '37', '131'
            - Or names: 'USA', 'UK', 'Japan'

            Reference values:
            - 213: USA
            - 37: UK
            - 131: Japan
            - 76: France
            - 102: Canada""",
            example="213",
            openapi_extra={"nullable": True}
        ),
        industry: str = Query(
            None,
            description="""Industry ID or name. Examples:
            - Use IDs: '56', '60', '69'
            - Or names: 'Finance', 'Energy', 'Healthcare'

            Reference values:
            - 32: Technology Hardware
            - 34: Software
            - 56: Finance
            - 60: Energy
            - 69: Healthcare""",
            example="56",
            openapi_extra={"nullable": True}
        ),
        # Company identifiers
        companyId: str = Query(
            None,
            description="Company ID (for any role in transaction). Examples: '21719', '29096'.",
            example="21719",
            openapi_extra={"nullable": True}
        ),
        company: str = Query(
            None,
            description="Alternative parameter for company ID. Examples: '456'.",
            example="456",
            openapi_extra={"nullable": True}
        ),
        companyName: str = Query(
            None,
            description="Company name search (partial match). Examples: 'Tech', 'Bank'.",
            example="Tech",
            openapi_extra={"nullable": True}
        ),
        involvedCompanyId: str = Query(
            None,
            description="Company ID that was involved in any role in the transaction. Examples: '972190', '18749'.",
            example="972190",
            openapi_extra={"nullable": True}
        ),
        # Transaction details
        transactionId: str = Query(
            None,
            description="Specific transaction ID for lookup. Examples: '12345'.",
            example="12345",
            openapi_extra={"nullable": True}
        ),
        transactionSize: str = Query(
            None,
            description="Transaction size/value. Supports operators: gte:, lte:, gt:, lt:, ne:, null:, notnull:. Examples: 'gte:1000000', 'notnull:'.",
            example="gte:1000000",
            openapi_extra={"nullable": True}
        ),
        size: str = Query(
            None,
            description="Alternative parameter for transaction size. Same format as transactionSize. Examples: 'gte:1000000'.",
            example="gte:1000000",
            openapi_extra={"nullable": True}
        ),
        statusId: str = Query(
            None,
            description="""Status ID or name. Examples:
            - Use IDs: '2', '1', '3'
            - Or names: 'Completed', 'Pending', 'Cancelled'

            Reference values:
            - 2: Completed
            - 1: Pending
            - 3: Cancelled""",
            example="2",
            openapi_extra={"nullable": True}
        ),
        # Currency related
        currencyId: str = Query(
            None,
            description="""Currency ID, name or ISO code. Examples:
            - Use IDs: '50', '49', '22'
            - Or names/codes: 'USD', 'Euro', 'GBP'

            Reference values:
            - 50: US Dollar (USD)
            - 49: Euro (EUR)
            - 22: British Pound (GBP)
            - 160: Other Currency""",
            example="50",
            openapi_extra={"nullable": True}
        ),
        currencyIsoCode: str = Query(
            None,
            description="Currency ISO code. Will be converted to currencyId. Examples: 'USD', 'EUR', 'GBP'.",
            example="USD",
            openapi_extra={"nullable": True}
        ),
        currencyName: str = Query(
            None,
            description="Currency name. Examples: 'US Dollar', 'Euro'.",
            example="US Dollar",
            openapi_extra={"nullable": True}
        ),
        # Relationship identifiers
        buyerId: str = Query(
            None,
            description="Buyer company ID. Examples: '29096', '21719'.",
            example="29096",
            openapi_extra={"nullable": True}
        ),
        sellerId: str = Query(
            None,
            description="Seller company ID. Examples: '112350'.",
            example="112350",
            openapi_extra={"nullable": True}
        ),
        targetId: str = Query(
            None,
            description="Target company ID. Examples: '789'.",
            example="789",
            openapi_extra={"nullable": True}
        ),
        acquirerId: str = Query(
            None,
            description="Acquirer company ID. Examples: '234'.",
            example="234",
            openapi_extra={"nullable": True}
        ),
        relationType: str = Query(
            None,
            description="""Relation type ID or name. Examples:
            - Use IDs: '1', '2'
            - Or names: 'Buyer-Target', 'Seller'

            Reference values:
            - 1: Buyer-Target
            - 2: Seller""",
            example="1",
            openapi_extra={"nullable": True}
        ),
        transactionToCompRelTypeId: str = Query(
            None,
            description="Transaction to company relationship type ID. Examples: '1'.",
            example="1",
            openapi_extra={"nullable": True}
        ),
        transactionToCompanyRelType: str = Query(
            None,
            description="Transaction to company relationship type name. Examples: 'Buyer'.",
            example="Buyer",
            openapi_extra={"nullable": True}
        ),
        # Related entity names
        targetCompanyName: str = Query(
            None,
            description="Target company name (for search). Examples: 'Target Corp'.",
            example="Target Corp",
            openapi_extra={"nullable": True}
        ),
        buyerCompanyName: str = Query(
            None,
            description="Buyer company name (for search). Examples: 'Buyer Inc'.",
            example="Buyer Inc",
            openapi_extra={"nullable": True}
        ),
        sellerCompanyName: str = Query(
            None,
            description="Seller company name (for search). Examples: 'Seller Ltd'.",
            example="Seller Ltd",
            openapi_extra={"nullable": True}
        ),
        involvedCompanyName: str = Query(
            None,
            description="Name of company involved in transaction. Examples: 'Involved Corp'.",
            example="Involved Corp",
            openapi_extra={"nullable": True}
        ),
        # Industry descriptors
        simpleIndustryDescription: str = Query(
            None,
            description="Simple industry description (for search). Examples: 'Technology', 'Healthcare'.",
            example="Technology",
            openapi_extra={"nullable": True}
        ),
        targetIndustryDescription: str = Query(
            None,
            description="Target company industry description. Examples: 'Software'.",
            example="Software",
            openapi_extra={"nullable": True}
        ),
        buyerIndustryDescription: str = Query(
            None,
            description="Buyer company industry description. Examples: 'Hardware'.",
            example="Hardware",
            openapi_extra={"nullable": True}
        ),
        # Transaction type name
        transactionIdTypeName: str = Query(
            None,
            description="Transaction type name. Examples: 'Acquisition', 'Buyback'.",
            example="Acquisition",
            openapi_extra={"nullable": True}
        ),
        # Cross filters (by country or industry for related entities)
        buyerCountry: str = Query(
            None,
            description="""Buyer company country ID or name. Examples:
            - Use IDs: '213', '37'
            - Or names: 'USA', 'UK'""",
            example="213",
            openapi_extra={"nullable": True}
        ),
        targetCountry: str = Query(
            None,
            description="""Target company country ID or name. Examples:
            - Use IDs: '37', '131'
            - Or names: 'UK', 'Japan'""",
            example="37",
            openapi_extra={"nullable": True}
        ),
        buyerIndustry: str = Query(
            None,
            description="""Buyer company industry ID or name. Examples:
            - Use IDs: '56', '58'
            - Or names: 'Finance', 'Technology'""",
            example="56",
            openapi_extra={"nullable": True}
        ),
        targetIndustry: str = Query(
            None,
            description="""Target company industry ID or name. Examples:
            - Use IDs: '34', '69'
            - Or names: 'Software', 'Healthcare'""",
            example="34",
            openapi_extra={"nullable": True}
        ),
        # Advisor related
        advisorId: str = Query(
            None,
            description="Advisor company ID. Examples: '398625'.",
            example="398625",
            openapi_extra={"nullable": True}
        ),
        advisorTypeId: str = Query(
            None,
            description="""Advisor type ID or name. Examples:
            - Use IDs: '2', '1'
            - Or names: 'Legal', 'Financial'

            Reference values:
            - 2: Legal
            - 1: Financial
            - 3: Consulting""",
            example="2",
            openapi_extra={"nullable": True}
        ),
        advisorCompanyName: str = Query(
            None,
            description="Advisor company name (for search). Examples: 'Legal Advisors Inc'.",
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
            description="Fields to group by (comma-separated). Used with aggregate functions in select. Examples: 'companyName', 'announcedYear,transactionIdTypeName'.",
            example="companyName",
            openapi_extra={"nullable": True}
        ),
        orderBy: str = Query(
            None,
            description="Fields to order by with direction (field:asc|desc). Comma-separated for multiple fields. Examples: 'transactionSize:desc', 'announcedYear:desc,announcedMonth:desc'.",
            example="transactionSize:desc",
            openapi_extra={"nullable": True}
        ),
        limit: int = Query(
            None,
            description="Maximum number of results to return. Examples: 10, 1, 20.",
            example=10,
            ge=1,
            openapi_extra={"nullable": True}
        ),
        offset: int = Query(
            None,
            description="Number of results to skip (for pagination). Examples: 0, 10, 20.",
            example=0,
            ge=0,
            openapi_extra={"nullable": True}
        ),
        # Special operation mode parameters
        count_only: bool = Query(
            False,
            description="Return only the count of matching transactions. Useful with COUNT() aggregations. Examples: true, false.",
            example=False
        ),
        page: int = Query(
            None,
            description="Page number for pagination. Used with page_size. Examples: 1, 2, 3.",
            example=1,
            ge=1,
            openapi_extra={"nullable": True}
        ),
        page_size: int = Query(
            None,
            description="Number of items per page for pagination. Used with page. Examples: 10, 20, 50.",
            example=10,
            ge=1,
            openapi_extra={"nullable": True}
        ),
        include_relationships: bool = Query(
            False,
            description="Include related company relationships in the response. Examples: true, false.",
            example=False
        ),
        include_advisors: bool = Query(
            False,
            description="Include transaction advisors in the response. Examples: true, false.",
            example=False
        ),
        includeAdvisors: str = Query(
            None,
            description="Alternative parameter to include advisors ('true'/'false'). Examples: 'true'.",
            example="true",
            openapi_extra={"nullable": True}
        ),
        # Analysis parameters
        analysisType: str = Query(
            None,
            description="Type of analysis to perform (e.g., 'trend', 'comparison'). Examples: 'trend'.",
            example="trend",
            openapi_extra={"nullable": True}
        ),
        fields: str = Query(
            None,
            description="Fields to include in analysis (comma-separated). Examples: 'year,month,size'.",
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