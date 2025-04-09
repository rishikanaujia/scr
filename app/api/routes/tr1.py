from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, status
from typing import Optional, List, Dict, Any

# Define API_PREFIX (replace with your actual prefix)
API_PREFIX = "/api/v1"

# Create your FastAPI app
app = FastAPI(title="Transactions API", description="API for retrieving transaction data")

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
    summary="Get Transactions",
    description="""
    Flexible transaction endpoint that supports various query parameters:
    - Filter fields: type, year, month, day, country, industry, company, size
    - Special operators: gte:, lte:, gt:, lt:, ne:, comma for IN
    - Query structure: select, groupBy, orderBy, limit, offset

    Examples:
    - /api/v1/transactions?type=1&year=gte:2020&groupBy=COMPANYNAME&orderBy=count:desc&limit=10
    - /api/v1/transactions?type=14&year=2021&country=131&orderBy=SIZE:desc&limit=20
    - /api/v1/transactions?industry=32,34&country=37&year=2023&orderBy=YEAR:desc,MONTH:desc,DAY:desc
    """
)
async def get_transactions(
        request: Request,
        # Define all parameters with OpenAPI schema manually set
        type: str = Query(
            None,
            description="Transaction type ID (e.g., '1' for Acquisitions)",
            example="1",
            openapi_extra={"nullable": True}
        ),
        year: str = Query(
            None,
            description="Announced year. Supports operators: gte:, lte:, gt:, lt:, ne:",
            example="gte:2020",
            openapi_extra={"nullable": True}
        ),
        month: str = Query(
            None,
            description="Announced month (1-12)",
            example="05",
            openapi_extra={"nullable": True}
        ),
        day: str = Query(
            None,
            description="Announced day (1-31)",
            example="15",
            openapi_extra={"nullable": True}
        ),
        country: str = Query(
            None,
            description="Country ID. Multiple values supported with comma separator.",
            example="131,147",
            openapi_extra={"nullable": True}
        ),
        industry: str = Query(
            None,
            description="Industry ID. Multiple values supported with comma separator.",
            example="32,34",
            openapi_extra={"nullable": True}
        ),
        company: str = Query(
            None,
            description="Company ID",
            example="456",
            openapi_extra={"nullable": True}
        ),
        companyName: str = Query(
            None,
            description="Company name search",
            example="Tech",
            openapi_extra={"nullable": True}
        ),
        size: str = Query(
            None,
            description="Transaction size. Supports operators: gte:, lte:, gt:, lt:, ne:",
            example="gte:1000000",
            openapi_extra={"nullable": True}
        ),
        select: str = Query(
            None,
            description="Fields to select (comma-separated)",
            example="YEAR,MONTH,SIZE,COMPANYNAME",
            openapi_extra={"nullable": True}
        ),
        groupBy: str = Query(
            None,
            description="Fields to group by (comma-separated)",
            example="YEAR,INDUSTRY",
            openapi_extra={"nullable": True}
        ),
        orderBy: str = Query(
            None,
            description="Fields to order by with direction (field:asc|desc)",
            example="SIZE:desc,YEAR:desc",
            openapi_extra={"nullable": True}
        ),
        limit: int = Query(
            None,
            description="Maximum number of results",
            example=20,
            ge=1,
            openapi_extra={"nullable": True}
        ),
        offset: int = Query(
            None,
            description="Number of results to skip",
            example=0,
            ge=0,
            openapi_extra={"nullable": True}
        ),
):
    try:
        # Get all query parameters including ones not explicitly listed
        params = dict(request.query_params)

        # Convert numeric parameters to strings if needed
        if limit is not None:
            params['limit'] = str(limit)
        if offset is not None:
            params['offset'] = str(offset)

        # Process request through controller with pagination
        result = await TransactionController.handle_request(
            request_params=params
        )

        # Return the result directly
        return result

    except QueryBuildError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Include the router
app.include_router(router)