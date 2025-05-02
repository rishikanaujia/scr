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
    [50 example queries shown in documentation]
    """
)
async def query_transactions(
        request: Request,

        # Basic filter parameters
        type: Optional[str] = Query(
            None,
            description="Transaction type ID (e.g., '1' for Acquisitions, '2' for M&A, '7' for Spin-Off, '10' for Fund Raise, '12' for Bankruptcy, '14' for Buybacks). Multiple values supported with comma separator.",
            example="2,14"
        ),
        year: Optional[str] = Query(
            None,
            description="Announced year. Supports operators: gte:, lte:, gt:, lt:, ne:, between:",
            example="gte:2020"
        ),
        month: Optional[str] = Query(
            None,
            description="Announced month (1-12)",
            example="05"
        ),
        day: Optional[str] = Query(
            None,
            description="Announced day (1-31)",
            example="15"
        ),
        country: Optional[str] = Query(
            None,
            description="Country ID. Multiple values supported with comma separator.",
            example="131,147"
        ),
        industry: Optional[str] = Query(
            None,
            description="Industry ID. Multiple values supported with comma separator.",
            example="32,34"
        ),

        # Company identification parameters
        companyId: Optional[str] = Query(
            None,
            description="Company ID",
            example="21719"
        ),
        companyName: Optional[str] = Query(
            None,
            description="Company name search",
            example="Tech"
        ),
        involvedCompanyId: Optional[str] = Query(
            None,
            description="ID of any company involved in the transaction",
            example="972190"
        ),

        # Transaction details
        transactionId: Optional[str] = Query(
            None,
            description="Transaction ID for direct lookup",
            example="12345"
        ),
        transactionSize: Optional[str] = Query(
            None,
            description="Transaction size. Supports operators: gte:, lte:, gt:, lt:, ne:, notnull:",
            example="gte:1000000"
        ),
        statusId: Optional[str] = Query(
            None,
            description="Status ID (e.g., '2' for Completed)",
            example="2"
        ),
        currencyId: Optional[str] = Query(
            None,
            description="Currency ID",
            example="50"
        ),
        currencyIsoCode: Optional[str] = Query(
            None,
            description="Currency ISO code (e.g., 'USD')",
            example="USD"
        ),

        # Relationship parameters
        relationType: Optional[str] = Query(
            None,
            description="Relationship type ID (e.g., '1' for acquisition, '2' for divestiture)",
            example="1"
        ),
        buyerId: Optional[str] = Query(
            None,
            description="Buyer company ID",
            example="29096"
        ),
        sellerId: Optional[str] = Query(
            None,
            description="Seller company ID",
            example="112350"
        ),
        targetId: Optional[str] = Query(
            None,
            description="Target company ID",
            example="123456"
        ),
        buyerCountry: Optional[str] = Query(
            None,
            description="Buyer's country ID",
            example="37,213"
        ),
        targetCountry: Optional[str] = Query(
            None,
            description="Target's country ID",
            example="213"
        ),
        buyerIndustry: Optional[str] = Query(
            None,
            description="Buyer's industry ID",
            example="61,62"
        ),
        targetIndustry: Optional[str] = Query(
            None,
            description="Target's industry ID",
            example="56"
        ),

        # Advisor parameters
        advisorId: Optional[str] = Query(
            None,
            description="Advisor company ID",
            example="398625"
        ),
        advisorTypeId: Optional[str] = Query(
            None,
            description="Advisor type ID (e.g., '2' for Legal advisor)",
            example="2"
        ),

        # Structure parameters
        select: Optional[str] = Query(
            None,
            description="Fields to select, including functions like COUNT, SUM, AVG, DISTINCT, and window functions",
            example="companyName,COUNT(transactionId) as dealCount"
        ),
        groupBy: Optional[str] = Query(
            None,
            description="Fields to group by (comma-separated)",
            example="simpleIndustryDescription"
        ),
        orderBy: Optional[str] = Query(
            None,
            description="Fields to order by with direction (field:asc|desc)",
            example="transactionSize:desc,announcedYear:desc"
        ),
        limit: Optional[int] = Query(
            None,
            description="Maximum number of results",
            example=10,
            ge=1
        ),
        offset: Optional[int] = Query(
            None,
            description="Number of results to skip",
            example=0,
            ge=0
        ),

        # Special operation modes
        count_only: bool = Query(
            False,
            description="Return only count of matching records"
        ),
        page: Optional[int] = Query(
            None,
            description="Page number for pagination",
            ge=1
        ),
        page_size: Optional[int] = Query(
            None,
            description="Results per page",
            ge=1
        ),
        include_relationships: bool = Query(
            False,
            description="Include related company relationships"
        ),
        include_advisors: bool = Query(
            False,
            description="Include transaction advisors"
        ),

        # Authentication dependency
        api_key: Dict = Depends(get_api_key)
):
    try:
        # Build params dictionary from explicitly defined parameters
        params = {}

        # Add all non-None parameters to the dictionary
        for param_name, param_value in {
            'type': type, 'year': year, 'month': month, 'day': day,
            'country': country, 'industry': industry, 'companyId': companyId,
            'companyName': companyName, 'involvedCompanyId': involvedCompanyId,
            'transactionId': transactionId, 'transactionSize': transactionSize,
            'statusId': statusId, 'currencyId': currencyId,
            'currencyIsoCode': currencyIsoCode, 'relationType': relationType,
            'buyerId': buyerId, 'sellerId': sellerId, 'targetId': targetId,
            'buyerCountry': buyerCountry, 'targetCountry': targetCountry,
            'buyerIndustry': buyerIndustry, 'targetIndustry': targetIndustry,
            'advisorId': advisorId, 'advisorTypeId': advisorTypeId,
            'select': select, 'groupBy': groupBy, 'orderBy': orderBy,
            'limit': limit, 'offset': offset
        }.items():
            if param_value is not None:
                params[param_name] = param_value

        # Handle special parameters
        if count_only:
            params['count_only'] = 'true'

        if page is not None:
            params['page'] = str(page)

        if page_size is not None:
            params['page_size'] = str(page_size)

        if include_relationships:
            params['include_relationships'] = 'true'

        if include_advisors:
            params['include_advisors'] = 'true'

        # Additional parameters from query params that weren't explicitly defined
        for key, value in request.query_params.items():
            if key not in params and key not in ['count_only', 'page', 'page_size',
                                                 'include_relationships', 'include_advisors']:
                params[key] = value

        # Continue with the original implementation logic
        # Check if it's a single transaction lookup by ID
        transaction_id = params.pop('transactionId', None)
        if transaction_id:
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

        # Handle special operation modes
        if count_only:
            count = await TransactionController.count_transactions(params)
            return {
                "data": [{"count": count}],
                "query_parameters": params,
                "timestamp": datetime.now().isoformat()
            }

        # Check if pagination is requested
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

        # Handle currency ISO code
        if 'currencyIsoCode' in params:
            iso_code = params.pop('currencyIsoCode')
            # Simulate lookup (in real code, this would query the database)
            currency_lookup = {"USD": "50"}
            if iso_code in currency_lookup:
                params['currencyId'] = currency_lookup[iso_code]

        # Handle special relationship parameters
        if 'relationType' in params:
            relation_type = params.pop('relationType')
            # Add the appropriate parameter for the filter parser
            params['transactionToCompRelTypeId'] = relation_type

        # Check for advisor relationships
        advisor_id = params.get('advisorId', None)
        advisor_type = params.get('advisorTypeId', None)
        if advisor_id or advisor_type:
            # Set flag to include advisor information
            params['includeAdvisors'] = 'true'

        # Execute the query
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