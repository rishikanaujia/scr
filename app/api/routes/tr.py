from fastapi import APIRouter, Query, Depends, HTTPException, Path, Body, Request, status
from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field

# Define API_PREFIX (replace with your actual prefix)
API_PREFIX = "/api/v1"


# Create the base model for transaction items
class TransactionItem(BaseModel):
    # Use Field with json_schema_extra to explicitly set nullable in OpenAPI
    COMPANYNAME: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    ID: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    TYPE: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    YEAR: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    MONTH: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    DAY: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    COUNTRY: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    INDUSTRY: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    COMPANY: Optional[str] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )
    SIZE: Optional[float] = Field(
        default=None,
        json_schema_extra={"nullable": True}
    )

    class Config:
        schema_extra = {
            "example": {
                "COMPANYNAME": "Example Corp",
                "ID": "123",
                "TYPE": "1",
                "YEAR": "2022",
                "MONTH": "05",
                "DAY": "15",
                "COUNTRY": "131",
                "INDUSTRY": "32",
                "COMPANY": "456",
                "SIZE": 1500000.00
            }
        }


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
    response_model=List[TransactionItem],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "COMPANYNAME": "LocalPaper.com LLC",
                            "ID": "123",
                            "TYPE": "1",
                            "YEAR": "2022",
                            "MONTH": "05",
                            "DAY": "15",
                            "COUNTRY": "131",
                            "INDUSTRY": "32"
                        },
                        {
                            "COMPANYNAME": "B2Digital, Incorporated",
                            "YEAR": "2022",
                            "TYPE": "2"
                        },
                        {
                            "COMPANYNAME": None,
                            "INDUSTRY": "32",
                            "SIZE": 1200000.00
                        }
                    ]
                }
            }
        },
        # Other responses remain the same
    }
)

async def get_transactions(
        request: Request,
        # Filter parameters with enhanced examples
        type: Optional[str] = Query(
            None,
            description="Transaction type ID (e.g., '1' for Acquisitions)",
            example="1"
        ),
        year: Optional[str] = Query(
            None,
            description="Announced year. Supports operators: gte:, lte:, gt:, lt:, ne:",
            example="gte:2020"
        ),
        month: Optional[str] = Query(None, description="Announced month (1-12)", example="05"),
        day: Optional[str] = Query(None, description="Announced day (1-31)", example="15"),
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
        company: Optional[str] = Query(None, description="Company ID", example="456"),
        companyName: Optional[str] = Query(None, description="Company name search", example="Tech"),
        size: Optional[str] = Query(
            None,
            description="Transaction size. Supports operators: gte:, lte:, gt:, lt:, ne:",
            example="gte:1000000"
        ),

        # Structure parameters
        select: Optional[str] = Query(
            None,
            description="Fields to select (comma-separated)",
            example="YEAR,MONTH,SIZE,COMPANYNAME"
        ),
        groupBy: Optional[str] = Query(
            None,
            description="Fields to group by (comma-separated)",
            example="YEAR,INDUSTRY"
        ),
        orderBy: Optional[str] = Query(
            None,
            description="Fields to order by with direction (field:asc|desc)",
            example="SIZE:desc,YEAR:desc"
        ),
        limit: Optional[int] = Query(
            None,
            description="Maximum number of results",
            example=20,
            ge=1
        ),
        offset: Optional[int] = Query(
            None,
            description="Number of results to skip",
            example=0,
            ge=0
        ),
):
    """
    Flexible transaction endpoint that supports various query parameters:
    - Filter fields: type, year, month, day, country, industry, company, size
    - Special operators: gte:, lte:, gt:, lt:, ne:, comma for IN
    - Query structure: select, groupBy, orderBy, limit, offset

    Examples:
    - /api/v1/transactions?type=1&year=gte:2020&groupBy=COMPANYNAME&orderBy=count:desc&limit=10
    - /api/v1/transactions?type=14&year=2021&country=131&orderBy=SIZE:desc&limit=20
    - /api/v1/transactions?industry=32,34&country=37&year=2023&orderBy=YEAR:desc,MONTH:desc,DAY:desc
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
        result = await TransactionController.handle_request(
            request_params=params
        )

        # Return the result directly
        return result

    except QueryBuildError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Add your router
app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="Your API Description",
        routes=app.routes,
    )

    # Loop through all components/schemas
    for schema_name, schema in openapi_schema["components"]["schemas"].items():
        if "properties" in schema:
            for prop_name, prop in schema["properties"].items():
                # If property uses anyOf with null, convert to nullable: true format
                if "anyOf" in prop:
                    types = [t["type"] for t in prop["anyOf"] if "type" in t and t["type"] != "null"]
                    if any(t["type"] == "null" for t in prop["anyOf"] if "type" in t):
                        # There's a null type in anyOf - convert to nullable: true
                        if len(types) == 1:
                            prop.pop("anyOf")
                            prop["type"] = types[0]
                            prop["nullable"] = True

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi