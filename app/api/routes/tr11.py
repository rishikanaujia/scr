"""API routes for transaction queries."""
from datetime import datetime
from typing import Dict, List, Any
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
    summary="Flexible Transaction Query Endpoint",
    description="""
    TRANSACTIONS API - QUERY PARAMETER REFERENCE
    ============================================

    A flexible transaction endpoint supporting various query parameters for filtering, grouping, and sorting.

    IMPORTANT: ALL IDs MUST BE NUMERIC
    ----------------------------------
    - Always use numeric IDs for: type, country, industry, currencyId, statusId, etc.
    - NEVER use text names like "Buybacks" or "USA" in place of their numeric IDs.
    - Example: Use `type=14` (not "Buybacks"), `country=213` (not "USA")

    ID REFERENCE TABLES
    ------------------
    Transaction Types:
      - 1: M&A
      - 2: Acquisitions 
      - 7: Spin-offs
      - 10: Fund Raises
      - 12: Bankruptcies
      - 14: Buybacks

    Countries:
      - 213: USA
      - 37: UK
      - 131: Japan
      - 147: Germany
      - 76: France
      - 102: Canada

    Industries:
      - 32, 34: Technology sectors
      - 56: Finance
      - 60: Energy
      - 69: Healthcare
      - 41: Manufacturing

    Currencies:
      - 50: USD
      - 49: EUR
      - 22: GBP
      - 160: Other currency

    Advisor Types:
      - 2: Legal

    Relation Types:
      - 1: Buyer-Target
      - 2: Seller

    PARAMETER OPERATORS
    ------------------
    - Equality: field=value
    - Greater/Less Than: field=gte:value, field=lte:value, field=gt:value, field=lt:value
    - Not Equal: field=ne:value
    - Between: field=between:value1,value2
    - Null/Not Null: field=null:, field=notnull:
    - Multiple Values: field=value1,value2,value3

    EXAMPLE URLS
    -----------
    1. Buybacks by Company:
       /transactions?type=14&companyId=21719&select=COUNT(transactionId) as count

    2. Acquisitions with Size Filter:
       /transactions?type=2&transactionSize=gte:1000000&orderBy=transactionSize:desc

    3. Complex Query with Window Function:
       /transactions?type=14&year=2017&country=7,16,99&select=SUM(transactionSize) OVER (PARTITION BY country) AS total

    4. Legal Advisors for Acquisitions:
       /transactions?companyId=34903&type=2&advisorTypeId=2&select=advisorCompanyName

    5. Transactions by Industry Group:
       /transactions?industry=32,34&groupBy=simpleIndustryDescription&select=simpleIndustryDescription,COUNT(transactionId) AS count

    6. Transactions with Cross-Filtering:
       /transactions?buyerIndustry=61&targetIndustry=56&select=transactionId,buyerCompanyName,targetCompanyName

    7. Multiple Transaction Types:
       /transactions?type=2,14&year=2022&select=transactionId,companyName,announcedDay

    Query Parameter Documentation Below
    ----------------------------------
    """,
    response_description="Returns transaction data based on the specified query parameters"
)
async def query_transactions(
        request: Request,
        # Transaction type and basic filters
        type: str = Query(
            None,
            description="NUMERIC Transaction type ID: 1=M&A, 2=Acquisitions, 7=Spin-offs, 10=Fund Raises, 12=Bankruptcies, 14=Buybacks. ONLY USE NUMERIC VALUES, NOT TEXT. Examples: '14' for Buybacks, '2,14' for both Acquisitions and Buybacks.",
            example="14",
            openapi_extra={"nullable": True}
        ),
        # Date filters
        year: str = Query(
            None,
            description="Year of announcement. Supports operators: gte:, lte:, gt:, lt:, ne:, between:, and comma-separated lists. Examples: '2022', 'gte:2020', 'between:2018,2021', '2020,2021,2022'.",
            example="2022",
            openapi_extra={"nullable": True}
        ),
        month: str = Query(
            None,
            description="Month of announcement (1-12). Supports operators and comma-separated lists. Examples: '1' for January, '1,2,3' for Q1.",
            example="3",
            openapi_extra={"nullable": True}
        ),
        day: str = Query(
            None,
            description="Day of announcement (1-31). Supports operators and comma-separated lists. Examples: '15', 'gte:20'.",
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
            description="NUMERIC Country ID. ALWAYS USE NUMERIC IDs: 213=USA, 37=UK, 131=Japan, 147=Germany, 76=France, 102=Canada. Multiple values supported with comma separator. Examples: '213' for USA, '37,131' for UK and Japan.",
            example="213",
            openapi_extra={"nullable": True}
        ),
        industry: str = Query(
            None,
            description="NUMERIC Industry ID. ALWAYS USE NUMERIC IDs: 32/34=Technology, 56=Finance, 60=Energy, 69=Healthcare, 41=Manufacturing. Multiple values supported with comma separator. Examples: '56' for Finance, '32,34' for Technology sectors.",
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
            description="NUMERIC Transaction status ID. ALWAYS USE NUMERIC IDs: 2=Completed. Examples: '2' for Completed.",
            example="2",
            openapi_extra={"nullable": True}
        ),
        # Currency related
        currencyId: str = Query(
            None,
            description="NUMERIC Currency ID. ALWAYS USE NUMERIC IDs: 50=USD, 49=EUR, 22=GBP, 160=Other. Examples: '50' for USD.",
            example="50",
            openapi_extra={"nullable": True}
        ),
        currencyIsoCode: str = Query(
            None,
            description="Currency ISO code (e.g., USD, EUR). Will be converted to currencyId. Examples: 'USD'.",
            example="USD",
            openapi_extra={"nullable": True}
        ),
        currencyName: str = Query(
            None,
            description="Currency name. Examples: 'US Dollar'.",
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
            description="NUMERIC Relation type ID. ALWAYS USE NUMERIC IDs: 1=Buyer-Target, 2=Seller. Examples: '1' for Buyer-Target relationships.",
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
            description="NUMERIC Buyer company country ID. ALWAYS USE NUMERIC IDs: 213=USA, 37=UK. Examples: '213' for USA.",
            example="213",
            openapi_extra={"nullable": True}
        ),
        targetCountry: str = Query(
            None,
            description="NUMERIC Target company country ID. ALWAYS USE NUMERIC IDs: 213=USA, 37=UK. Examples: '37' for UK.",
            example="37",
            openapi_extra={"nullable": True}
        ),
        buyerIndustry: str = Query(
            None,
            description="NUMERIC Buyer company industry ID. ALWAYS USE NUMERIC IDs: 56=Finance, 61=Technology. Examples: '56' for Finance sector.",
            example="56",
            openapi_extra={"nullable": True}
        ),
        targetIndustry: str = Query(
            None,
            description="NUMERIC Target company industry ID. ALWAYS USE NUMERIC IDs: 56=Finance, 61=Technology. Examples: '61' for Technology sector.",
            example="61",
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
            description="NUMERIC Advisor type ID. ALWAYS USE NUMERIC IDs: 2=Legal. Examples: '2' for Legal advisors.",
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
            - Window functions: 'SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue'
            Examples: 'transactionId,companyName', 'COUNT(transactionId) as count'""",
            example="companyName,COUNT(transactionId) AS count",
            openapi_extra={"nullable": True}
        ),
        groupBy: str = Query(
            None,
            description="Fields to group by (comma-separated). Used with aggregate functions in select. Examples: 'companyName', 'announcedYear,transactionIdTypeName', 'simpleIndustryDescription'.",
            example="companyName",
            openapi_extra={"nullable": True}
        ),
        orderBy: str = Query(
            None,
            description="Fields to order by with direction (field:asc|desc). Comma-separated for multiple fields. Examples: 'transactionSize:desc', 'announcedYear:desc,announcedMonth:desc,announcedDay:desc'.",
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