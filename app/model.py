"""Pydantic models for request/response schemas."""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.config.settings import settings


# Base models
class BaseResponse(BaseModel):
    """Base class for all response models."""

    class Config:
        """Pydantic configuration."""
        allow_population_by_field_name = True
        orm_mode = True


# API Documentation models
class EndpointInfo(BaseModel):
    """Information about an API endpoint."""
    id: str = Field(..., description="Unique identifier for the endpoint")
    name: str = Field(..., description="Endpoint name")
    description: str = Field(..., description="Endpoint description")


class EndpointSchema(BaseModel):
    """Schema information for an API endpoint."""
    id: str = Field(..., description="Unique identifier for the endpoint schema")
    name: str = Field(..., description="Schema name")
    description: str = Field(..., description="Schema description")
    required_params: List[str] = Field(..., description="List of required parameters")
    allowed_params: List[str] = Field(..., description="List of all allowed parameters")

    class Config:
        allow_population_by_field_name = True


# Query Parameters Models
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: Optional[int] = Field(
        None,
        ge=1,
        le=settings.MAX_LIMIT,
        description="Items per page (default: settings.DEFAULT_LIMIT)"
    )

    class Config:
        allow_population_by_field_name = True


class QueryParams(BaseModel):
    """Internal representation of query parameters."""
    select: Optional[List[str]] = Field(None, description="Fields to select")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filter conditions")
    joins: Optional[List[str]] = Field(None, description="Tables to join")
    group_by: Optional[List[str]] = Field(None, description="Fields to group by")
    order_by: Optional[Dict[str, str]] = Field(None, description="Sort order (field: direction)")
    limit: Optional[int] = Field(None, ge=1, description="Maximum number of results")
    offset: Optional[int] = Field(None, ge=0, description="Number of results to skip")

    class Config:
        allow_population_by_field_name = True


class TransactionQueryParams(BaseModel):
    """Query parameters for transaction endpoint."""
    # Filter parameters
    type: Optional[str] = Field(None, description="Transaction type ID")
    year: Optional[str] = Field(None, description="Announced year")
    month: Optional[str] = Field(None, description="Announced month")
    day: Optional[str] = Field(None, description="Announced day")
    country: Optional[str] = Field(None, description="Country ID")
    industry: Optional[str] = Field(None, description="Industry ID")
    company: Optional[str] = Field(None, description="Company ID")
    company_name: Optional[str] = Field(None, alias="companyName", description="Company name")
    size: Optional[str] = Field(None, description="Transaction size")

    # Structure parameters
    select: Optional[str] = Field(None, description="Fields to select (comma-separated)")
    group_by: Optional[str] = Field(None, alias="groupBy", description="Fields to group by (comma-separated)")
    order_by: Optional[str] = Field(None, alias="orderBy",
                                    description="Fields to order by with direction (field:asc|desc)")
    limit: Optional[int] = Field(None, ge=1, description="Maximum number of results")
    offset: Optional[int] = Field(None, ge=0, description="Number of results to skip")

    class Config:
        allow_population_by_field_name = True

    @validator('limit')
    def validate_limit(cls, v):
        """Validate that limit doesn't exceed MAX_LIMIT."""
        if v is not None and v > settings.MAX_LIMIT:
            return settings.MAX_LIMIT
        return v


class AnalysisParams(BaseModel):
    """Parameters for transaction analysis endpoint."""
    analysis_type: str = Field(
        ...,
        description="Type of analysis to perform: trend, comparison, distribution"
    )
    fields: Optional[List[str]] = Field(None, description="Fields to analyze")

    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        """Validate analysis type is one of the allowed values."""
        allowed_types = ["trend", "comparison", "distribution"]
        if v not in allowed_types:
            raise ValueError(f"analysis_type must be one of: {', '.join(allowed_types)}")
        return v

    class Config:
        allow_population_by_field_name = True


# Response Models
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        allow_population_by_field_name = True


class TransactionSummary(BaseResponse):
    """Summary of transaction data."""
    year: int = Field(..., description="Transaction year")
    total_transactions: int = Field(..., alias="totalTransactions", description="Total number of transactions")
    total_value: Optional[float] = Field(None, alias="totalValue", description="Total transaction value")
    average_value: Optional[float] = Field(None, alias="averageValue", description="Average transaction value")
    min_value: Optional[float] = Field(None, alias="minValue", description="Minimum transaction value")
    max_value: Optional[float] = Field(None, alias="maxValue", description="Maximum transaction value")
    unique_companies: Optional[int] = Field(None, alias="uniqueCompanies", description="Number of unique companies")


class TransactionDetail(BaseResponse):
    """Detailed transaction information."""
    transaction_id: str = Field(..., alias="transactionId", description="Unique transaction ID")
    company_name: Optional[str] = Field(None, alias="companyName", description="Company name")
    announced_date: Optional[datetime] = Field(None, alias="announcedDate", description="Full announced date")
    announced_year: Optional[int] = Field(None, alias="announcedYear", description="Year of announcement")
    announced_month: Optional[int] = Field(None, alias="announcedMonth", description="Month of announcement")
    announced_day: Optional[int] = Field(None, alias="announcedDay", description="Day of announcement")
    transaction_size: Optional[float] = Field(None, alias="transactionSize", description="Transaction size/value")
    transaction_type_name: Optional[str] = Field(None, alias="transactionIdTypeName", description="Type of transaction")
    status_id: Optional[int] = Field(None, alias="statusId", description="Status ID")
    currency_id: Optional[str] = Field(None, alias="currencyId", description="Currency ID")


class TransactionListResponse(BaseResponse):
    """Response model for transaction list endpoint."""
    data: List[Dict[str, Any]] = Field(..., description="List of transactions")
    count: int = Field(..., description="Total number of results")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the query")


class RelatedCompanyInfo(BaseResponse):
    """Information about a company related to a transaction."""
    company_id: int = Field(..., alias="companyId", description="Company ID")
    company_name: str = Field(..., alias="companyName", description="Company name")
    role: str = Field(..., description="Role in the transaction (acquirer, target, etc.)")
    country_id: Optional[int] = Field(None, alias="countryId", description="Country ID")
    country_name: Optional[str] = Field(None, alias="countryName", description="Country name")
    industry_id: Optional[int] = Field(None, alias="industryId", description="Industry ID")
    industry_name: Optional[str] = Field(None, alias="industryName", description="Industry name")


class AdvisorInfo(BaseResponse):
    """Information about a transaction advisor."""
    advisor_id: int = Field(..., alias="advisorId", description="Advisor ID")
    advisor_name: str = Field(..., alias="advisorName", description="Advisor name")
    advisor_type: str = Field(..., alias="advisorType", description="Advisor type")
    client_company_id: Optional[int] = Field(None, alias="clientCompanyId", description="Client company ID")
    client_company_name: Optional[str] = Field(None, alias="clientCompanyName", description="Client company name")


class TransactionDetailResponse(BaseResponse):
    """Detailed response for a single transaction."""
    transaction: TransactionDetail = Field(..., description="Transaction details")
    companies: Optional[List[RelatedCompanyInfo]] = Field(None, description="Related companies")
    advisors: Optional[List[AdvisorInfo]] = Field(None, description="Transaction advisors")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AnalysisResponse(BaseResponse):
    """Response for transaction analysis."""
    analysis_type: str = Field(..., alias="analysisType", description="Type of analysis performed")
    data: List[Dict[str, Any]] = Field(..., description="Analysis results")
    summary: Optional[Dict[str, Any]] = Field(None, description="Summary statistics")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters used for the analysis")


class SchemaInfo(BaseResponse):
    """Information about a database schema element."""
    name: str = Field(..., description="Schema element name")
    type: str = Field(..., description="Schema element type")
    description: Optional[str] = Field(None, description="Description")
    fields: Optional[List[Dict[str, Any]]] = Field(None, description="Fields if applicable")