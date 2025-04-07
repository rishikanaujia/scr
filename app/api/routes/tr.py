from fastapi import APIRouter, Query, Depends, HTTPException, Path, Body, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Response models
class TransactionItem(BaseModel):
    id: str
    type: str
    year: str
    month: str
    day: str
    country: str
    industry: str
    company: str
    companyName: str
    size: float

    # Add other fields

    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "type": "1",
                "year": "2022",
                "month": "05",
                "day": "15",
                "country": "131",
                "industry": "32",
                "company": "456",
                "companyName": "Example Corp",
                "size": 1500000.00
            }
        }


class TransactionResponse(BaseModel):
    data: List[TransactionItem]
    count: int
    total: int


class ErrorResponse(BaseModel):
    detail: str


# Create router
router = APIRouter(
    prefix=f"{API_PREFIX}",
    tags=["transactions"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.get(
    "/transactions",
    response_model=TransactionResponse,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "123",
                                "type": "1",
                                "year": "2022",
                                "month": "05",
                                "day": "15",
                                "country": "131",
                                "industry": "32",
                                "company": "456",
                                "companyName": "Example Corp",
                                "size": 1500000.00
                            }
                        ],
                        "count": 1,
                        "total": 100
                    }
                }
            }
        }
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
            example="year,month,size,companyName"
        ),
        groupBy: Optional[str] = Query(
            None,
            description="Fields to group by (comma-separated)",
            example="year,industry"
        ),
        orderBy: Optional[str] = Query(
            None,
            description="Fields to order by with direction (field:asc|desc)",
            example="size:desc,year:desc"
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
        return await TransactionController.handle_request(
            request_params=params
        )
    except QueryBuildError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))