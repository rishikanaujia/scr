"""
Main FastAPI application file.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import transaction_routes
from app.config.settings import settings

# Initialize the FastAPI application
app = FastAPI(
    title="Transaction API",
    description="""
    # Transaction API

    This API provides access to transaction data with a flexible query interface that supports both IDs and human-readable names.

    ## Key Features

    - **Flexible Parameters**: Use numeric IDs (`type=14`) or human-readable names (`type=Buyback`)
    - **Advanced Filtering**: Apply operators like `gte:`, `between:`, `notnull:`, and more
    - **SQL-like Functions**: Use `COUNT()`, `SUM()`, `AVG()`, and window functions
    - **Grouping & Sorting**: Group results and order them by any field

    ## Documentation Resources

    - **/transactions/examples**: View a comprehensive list of example API queries
    - **/transactions/reference**: See all available values for transaction types, countries, industries, etc.

    ## Common Query Patterns

    ```
    # Query with IDs
    /api/v1/transactions?type=14&country=213&year=2022

    # Same query with names
    /api/v1/transactions?type=Buyback&country=USA&year=2022

    # Complex aggregation query
    /api/v1/transactions?type=2&industry=56&groupBy=country&select=country,COUNT(transactionId) as count&orderBy=count:desc
    ```

    Refer to the **/transactions/examples** endpoint for a complete set of example queries.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transaction_routes.router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Transaction API - Use /api/docs for interactive documentation"
    }


# Testing and debugging endpoint
if settings.ENVIRONMENT == "development":
    @app.get("/api/test")
    async def test_endpoint():
        from app.utils.id_name_mapper import IDNameMapper

        # Test the ID-Name mapper
        return {
            "transaction_types": {
                "id_to_name": {
                    "14": IDNameMapper.get_transaction_type_name(14),
                    "2": IDNameMapper.get_transaction_type_name(2)
                },
                "name_to_id": {
                    "Buyback": IDNameMapper.get_transaction_type_id("Buyback"),
                    "acquisition": IDNameMapper.get_transaction_type_id("acquisition")
                }
            },
            "countries": {
                "id_to_name": {
                    "213": IDNameMapper.get_country_name(213),
                    "37": IDNameMapper.get_country_name(37)
                },
                "name_to_id": {
                    "USA": IDNameMapper.get_country_id("USA"),
                    "uk": IDNameMapper.get_country_id("uk")
                }
            }
        }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )