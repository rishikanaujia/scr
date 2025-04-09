from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, status
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi.openapi.utils import get_openapi

# Assuming these are imported elsewhere
# from your_error_module import QueryBuildError, DatabaseError
# from your_controller_module import TransactionController

# Define API_PREFIX
API_PREFIX = "/api/v1"

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
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response - format varies based on query parameters",
            "content": {
                "application/json": {
                    "examples": {
                        "standard": {
                            "summary": "Standard listing",
                            "value": {
                                "data": [
                                    {
                                        "COMPANYNAME": "Example Corp",
                                        "ID": "123",
                                        "TYPE": "1",
                                        "YEAR": "2022"
                                    },
                                    {
                                        "COMPANYNAME": "Another LLC",
                                        "ID": "456",
                                        "TYPE": "2",
                                        "YEAR": "2023"
                                    }
                                ],
                                "query_parameters": {
                                    "type": "1",
                                    "year": "gte:2020",
                                    "limit": "20"
                                },
                                "timestamp": "2025-04-09T14:32:45.123456"
                            }
                        },
                        "grouped": {
                            "summary": "Grouped by year",
                            "value": {
                                "data": [
                                    {
                                        "YEAR": "2022",
                                        "count": 15,
                                        "total_size": 2500000
                                    },
                                    {
                                        "YEAR": "2023",
                                        "count": 23,
                                        "total_size": 3800000
                                    }
                                ],
                                "query_parameters": {
                                    "groupBy": "YEAR",
                                    "orderBy": "count:desc"
                                },
                                "timestamp": "2025-04-09T14:33:12.654321"
                            }
                        },
                        "selected": {
                            "summary": "Selected fields only",
                            "value": {
                                "data": [
                                    {
                                        "COMPANYNAME": "Example Corp",
                                        "SIZE": 1500000
                                    },
                                    {
                                        "COMPANYNAME": "Another LLC",
                                        "SIZE": 2300000
                                    }
                                ],
                                "query_parameters": {
                                    "select": "COMPANYNAME,SIZE",
                                    "orderBy": "SIZE:desc"
                                },
                                "timestamp": "2025-04-09T14:34:23.789012"
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid filter parameter"
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Database connection error"
                    }
                }
            }
        }
    }
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

        # Create a response that includes both the data and query parameters
        response = {
            "data": result,
            "query_parameters": params,
            "timestamp": datetime.now().isoformat()
        }

        # Return the enhanced response
        return response

    except QueryBuildError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Create FastAPI app
app = FastAPI(title="Transactions API", description="API for retrieving transaction data")

# Include the router
app.include_router(router)


# Custom OpenAPI schema function to enforce nullable:true format
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Process operation parameters
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "parameters" in operation:
                for parameter in operation["parameters"]:
                    if "schema" in parameter and "anyOf" in parameter["schema"]:
                        types = [t["type"] for t in parameter["schema"]["anyOf"] if "type" in t and t["type"] != "null"]
                        if any(t["type"] == "null" for t in parameter["schema"]["anyOf"] if "type" in t):
                            if len(types) == 1:
                                parameter["schema"].pop("anyOf")
                                parameter["schema"]["type"] = types[0]
                                parameter["schema"]["nullable"] = True

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi