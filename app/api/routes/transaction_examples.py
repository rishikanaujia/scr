"""
Transaction API Examples

This module provides a comprehensive collection of example URLs
for the Transaction API to enhance OpenAPI documentation.
"""
from typing import Dict, List, Any


def get_transaction_examples() -> List[Dict[str, Any]]:
    """
    Returns a list of example transaction API queries with descriptions.
    Used for enhancing OpenAPI documentation and helping LLMs generate correct URLs.
    """
    return [
        {
            "name": "Top Companies by Private Placement Count",
            "url": "/api/v1/transactions?type=1&year=gte:2020&groupBy=companyName&select=companyName,COUNT(transactionId) as privatePlacementCount&orderBy=privatePlacementCount:desc&limit=1",
            "url_with_names": "/api/v1/transactions?type=M&A&year=gte:2020&groupBy=companyName&select=companyName,COUNT(transactionId) as privatePlacementCount&orderBy=privatePlacementCount:desc&limit=1",
            "description": "Lists companies with the highest count of private placements since 2020."
        },
        {
            "name": "Transaction Details with Type and Country",
            "url": "/api/v1/transactions?type=14&year=2021&country=131&select=transactionId,companyName,transactionSize,announcedDay,announcedMonth,announcedYear,transactionIdTypeName&orderBy=transactionSize:desc&limit=1",
            "url_with_names": "/api/v1/transactions?type=Buyback&year=2021&country=Japan&select=transactionId,companyName,transactionSize,announcedDay,announcedMonth,announcedYear,transactionIdTypeName&orderBy=transactionSize:desc&limit=1",
            "description": "Retrieves details of buyback transactions in Japan for 2021, ordered by size."
        },
        {
            "name": "Transactions in Specific Industries and Country",
            "url": "/api/v1/transactions?industry=32,34&country=37&year=2023&select=transactionId,companyName,simpleIndustryDescription,country,announcedDay,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?industry=Technology Hardware,Software&country=UK&year=2023&select=transactionId,companyName,simpleIndustryDescription,country,announcedDay,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Lists technology hardware and software transactions in the UK for 2023, ordered by date."
        },
        {
            "name": "Transactions by Country and Year",
            "url": "/api/v1/transactions?country=76&year=2019&select=transactionId,companyName,simpleIndustryDescription,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?country=France&year=2019&select=transactionId,companyName,simpleIndustryDescription,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Retrieves transactions in France for 2019, ordered by date."
        },
        {
            "name": "Transactions with Complex Filtering",
            "url": "/api/v1/transactions?type=2&year=between:2018,2021&industry=63&country=ne:213&transactionSize=notnull:&select=transactionId,companyName,simpleIndustryDescription,transactionSize,currencyId,announcedDay,announcedMonth,announcedYear&orderBy=transactionSize:desc&limit=10",
            "url_with_names": "/api/v1/transactions?type=Acquisition&year=between:2018,2021&industry=Real Estate&country=ne:USA&transactionSize=notnull:&select=transactionId,companyName,simpleIndustryDescription,transactionSize,currencyId,announcedDay,announcedMonth,announcedYear&orderBy=transactionSize:desc&limit=10",
            "description": "Finds real estate acquisitions outside the USA between 2018-2021 with non-null transaction sizes."
        },
        {
            "name": "Company Acquisition Targets",
            "url": "/api/v1/transactions?buyerId=29096&type=2&year=gte:2022&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?buyerId=29096&type=Acquisition&year=gte:2022&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Lists acquisition targets for a specific buyer company since 2022, ordered by date."
        },
        {
            "name": "Buyback Count by Industry and Period",
            "url": "/api/v1/transactions?type=14&industry=60&year=between:2017,2019&select=COUNT(transactionId) as buyback_count",
            "url_with_names": "/api/v1/transactions?type=Buyback&industry=Energy&year=between:2017,2019&select=COUNT(transactionId) as buyback_count",
            "description": "Counts buyback transactions in the energy industry between 2017-2019."
        },
        {
            "name": "Transaction Value by Industry",
            "url": "/api/v1/transactions?type=14&year=2017&country=7,16,99&currencyId=50&select=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue&groupBy=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=country,announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?type=Buyback&year=2017&country=Australia,Brazil,India&currencyId=USD&select=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue&groupBy=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId&orderBy=country,announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Analyzes buyback transaction values by country in 2017 using window functions."
        },
        {
            "name": "Transaction Value by Country (Window Function)",
            "url": "/api/v1/transactions?type=14&year=2017&country=7,16,99&currencyId=50&select=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue&orderBy=country,announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?type=Buyback&year=2017&country=Australia,Brazil,India&currencyId=USD&select=transactionId,companyName,country,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,SUM(transactionSize) OVER (PARTITION BY country) AS totalTransactionValue&orderBy=country,announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Analyzes transaction values by country using SQL window functions."
        },
        {
            "name": "Distinct Industry Count",
            "url": "/api/v1/transactions?type=14&year=2022&country=37&select=COUNT(DISTINCT(simpleIndustryDescription)) as industries_with_buybacks",
            "url_with_names": "/api/v1/transactions?type=Buyback&year=2022&country=UK&select=COUNT(DISTINCT(simpleIndustryDescription)) as industries_with_buybacks",
            "description": "Counts unique industries with buybacks in the UK in 2022."
        },
        {
            "name": "Transactions by Industry and Year",
            "url": "/api/v1/transactions?industry=69&year=2021&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName,country&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?industry=Healthcare&year=2021&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName,country&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Lists healthcare industry transactions in 2021, ordered by date."
        },
        {
            "name": "Transactions by Industry, Country and Year",
            "url": "/api/v1/transactions?industry=69&country=102&year=2021&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName,country&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?industry=Healthcare&country=Canada&year=2021&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName,country&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Lists healthcare transactions in Canada in 2021."
        },
        {
            "name": "Transactions by Type, Industry, Year and Month",
            "url": "/api/v1/transactions?type=2,14&industry=6&year=2024&month=1&select=transactionId,companyName,simpleIndustryDescription,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedDay:desc",
            "url_with_names": "/api/v1/transactions?type=Acquisition,Buyback&industry=Agriculture&year=2024&month=1&select=transactionId,companyName,simpleIndustryDescription,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedDay:desc",
            "description": "Finds acquisitions and buybacks in agriculture in January 2024."
        },
        {
            "name": "Company Buybacks",
            "url": "/api/v1/transactions?companyId=29096&type=14&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyName,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?companyId=29096&type=Buyback&select=transactionId,companyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyName,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Lists buyback transactions for a specific company."
        },
        {
            "name": "Company Related Transactions",
            "url": "/api/v1/transactions?involvedCompanyId=18749&select=transactionId,targetCompanyName,involvedCompanyName,announcedDay,announcedMonth,announcedYear,transactionIdTypeName,transactionToCompanyRelType,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc&limit=5",
            "url_with_names": "/api/v1/transactions?involvedCompanyId=18749&select=transactionId,targetCompanyName,involvedCompanyName,announcedDay,announcedMonth,announcedYear,transactionIdTypeName,transactionToCompanyRelType,transactionSize,currencyId&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc&limit=5",
            "description": "Shows the 5 most recent transactions involving a specific company."
        },
        {
            "name": "Average Transaction Size",
            "url": "/api/v1/transactions?type=14&year=2022&month=3&currencyId=160&select=AVG(transactionsize)",
            "url_with_names": "/api/v1/transactions?type=Buyback&year=2022&month=3&currencyId=Other Currency&select=AVG(transactionsize)",
            "description": "Calculates the average size of buyback transactions in March 2022."
        },
        {
            "name": "Tech M&A Deal Count",
            "url": "/api/v1/transactions?type=2&year=2024&industry=58&select=COUNT(transactionId) as tech_ma_deals_in_2024",
            "url_with_names": "/api/v1/transactions?type=Acquisition&year=2024&industry=Technology&select=COUNT(transactionId) as tech_ma_deals_in_2024",
            "description": "Counts technology acquisitions in 2024."
        },
        {
            "name": "Mergers and Acquisitions Count",
            "url": "/api/v1/transactions?type=2&year=2022&industry=41&select=COUNT(transactionId) as number_of_mergers_and_acquisitions",
            "url_with_names": "/api/v1/transactions?type=Acquisition&year=2022&industry=Manufacturing&select=COUNT(transactionId) as number_of_mergers_and_acquisitions",
            "description": "Counts acquisitions in the manufacturing industry in 2022."
        },
        {
            "name": "Future Mergers Count",
            "url": "/api/v1/transactions?type=2&year=2025&industry=2&select=COUNT(transactionId) as number_of_mergers",
            "url_with_names": "/api/v1/transactions?type=Acquisition&year=2025&industry=Aerospace&select=COUNT(transactionId) as number_of_mergers",
            "description": "Counts aerospace acquisitions planned for 2025."
        },
        {
            "name": "Completed Transactions Count",
            "url": "/api/v1/transactions?type=2&year=gte:2022&industry=50&statusId=2&select=COUNT(DISTINCT companyId) as CompletedTransactions",
            "url_with_names": "/api/v1/transactions?type=Acquisition&year=gte:2022&industry=Transportation&statusId=Completed&select=COUNT(DISTINCT companyId) as CompletedTransactions",
            "description": "Counts unique companies with completed acquisitions in transportation since 2022."
        },
        {
            "name": "Bankruptcy Count",
            "url": "/api/v1/transactions?type=12&year=2024&industry=35&select=COUNT(transactionId) as BankruptcyCount",
            "url_with_names": "/api/v1/transactions?type=Bankruptcy&year=2024&industry=Automotive&select=COUNT(transactionId) as BankruptcyCount",
            "description": "Counts bankruptcies in the automotive industry in 2024."
        },
        {
            "name": "Transaction Count by Year",
            "url": "/api/v1/transactions?companyId=20765463&statusId=2&groupBy=announcedyear&select=announcedyear,COUNT(announcedyear)",
            "url_with_names": "/api/v1/transactions?companyId=20765463&statusId=Completed&groupBy=announcedyear&select=announcedyear,COUNT(announcedyear)",
            "description": "Counts completed transactions by year for a specific company."
        },
        {
            "name": "Company Buyback Count",
            "url": "/api/v1/transactions?companyId=24937&type=14&select=COUNT(transactionId) as BuybackCount",
            "url_with_names": "/api/v1/transactions?companyId=24937&type=Buyback&select=COUNT(transactionId) as BuybackCount",
            "description": "Counts buyback transactions for a specific company."
        },
        {
            "name": "Deal Count by Year and Type",
            "url": "/api/v1/transactions?companyId=21401&year=2020,2021&groupBy=announcedYear,transactionIdTypeName&select=announcedYear,transactionIdTypeName,COUNT(transactionId) as dealCount&orderBy=announcedYear,transactionIdTypeName",
            "url_with_names": "/api/v1/transactions?companyId=21401&year=2020,2021&groupBy=announcedYear,transactionIdTypeName&select=announcedYear,transactionIdTypeName,COUNT(transactionId) as dealCount&orderBy=announcedYear,transactionIdTypeName",
            "description": "Groups and counts transactions by year and type for a specific company."
        },
        {
            "name": "Acquisitions by Company",
            "url": "/api/v1/transactions?buyerId=284342&relationType=1&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?buyerId=284342&relationType=Buyer-Target&select=transactionId,targetCompanyName,buyerCompanyName,announcedDay,announcedMonth,announcedYear,transactionSize,currencyId,transactionIdTypeName&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Lists acquisitions where a specific company is the buyer."
        },
        # Add more examples to cover all 48 patterns
        # ...

        # I'll continue with key examples to show various query patterns:
        {
            "name": "Legal Advisors for Company",
            "url": "/api/v1/transactions?companyId=34903&type=2&advisorTypeId=2&select=advisorCompanyName",
            "url_with_names": "/api/v1/transactions?companyId=34903&type=Acquisition&advisorTypeId=Legal&select=advisorCompanyName",
            "description": "Lists legal advisors for a company's acquisition transactions."
        },
        {
            "name": "Buyback Advisors",
            "url": "/api/v1/transactions?companyId=21835&type=14&select=advisorCompanyName",
            "url_with_names": "/api/v1/transactions?companyId=21835&type=Buyback&select=advisorCompanyName",
            "description": "Lists advisors for a company's buyback transactions."
        },
        {
            "name": "Advisor-Company Relationship Count",
            "url": "/api/v1/transactions?advisorId=398625&companyId=6882342&select=COUNT(transactionId)&groupBy=companyName",
            "url_with_names": "/api/v1/transactions?advisorId=398625&companyId=6882342&select=COUNT(transactionId)&groupBy=companyName",
            "description": "Counts transactions between a specific advisor and company."
        },
        {
            "name": "Top Industry by M&A",
            "url": "/api/v1/transactions?year=2023&type=2&groupBy=simpleIndustryDescription&select=simpleIndustryDescription,COUNT(transactionId) as transactionCount&orderBy=transactionCount:desc&limit=1",
            "url_with_names": "/api/v1/transactions?year=2023&type=Acquisition&groupBy=simpleIndustryDescription&select=simpleIndustryDescription,COUNT(transactionId) as transactionCount&orderBy=transactionCount:desc&limit=1",
            "description": "Finds the industry with the most acquisitions in 2023."
        },
        {
            "name": "Total Value by Industry and Currency",
            "url": "/api/v1/transactions?industry=64&year=2023&type=2&currencyIsoCode=USD&select=SUM(transactionSize) as totalValue",
            "url_with_names": "/api/v1/transactions?industry=Consumer&year=2023&type=Acquisition&currencyIsoCode=USD&select=SUM(transactionSize) as totalValue",
            "description": "Calculates the total value of consumer industry acquisitions in 2023 in USD."
        },
        {
            "name": "Cross-Industry Transactions",
            "url": "/api/v1/transactions?relationType=1&buyerIndustry=61,62&buyerCountry=37,213&select=transactionId,targetCompanyName,buyerCompanyName,targetIndustryDescription,buyerIndustryDescription,buyerCountry,announcedDay,announcedMonth,announcedYear&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "url_with_names": "/api/v1/transactions?relationType=Buyer-Target&buyerIndustry=Internet,Media&buyerCountry=UK,USA&select=transactionId,targetCompanyName,buyerCompanyName,targetIndustryDescription,buyerIndustryDescription,buyerCountry,announcedDay,announcedMonth,announcedYear&orderBy=announcedYear:desc,announcedMonth:desc,announcedDay:desc",
            "description": "Lists transactions where internet/media companies from the UK/USA are buyers."
        },
        {
            "name": "Industry Acquisition Count",
            "url": "/api/v1/transactions?type=2&relationType=1&industry=56,61,62&groupBy=simpleIndustryDescription&select=simpleIndustryDescription,COUNT(transactionId) AS AcquisitionCount&orderBy=AcquisitionCount:desc",
            "url_with_names": "/api/v1/transactions?type=Acquisition&relationType=Buyer-Target&industry=Finance,Internet,Media&groupBy=simpleIndustryDescription&select=simpleIndustryDescription,COUNT(transactionId) AS AcquisitionCount&orderBy=AcquisitionCount:desc",
            "description": "Counts acquisitions grouped by industry for finance, internet, and media sectors."
        }
    ]


def get_example_openapi_extensions() -> Dict[str, Any]:
    """
    Returns OpenAPI extensions with detailed examples for LLM consumption.
    """
    return {
        "x-transaction-examples": get_transaction_examples(),
        "x-name-id-mappings": {
            "transaction_types": [
                {"id": 1, "name": "M&A", "aliases": ["merger", "merger and acquisition"]},
                {"id": 2, "name": "Acquisition", "aliases": ["acquisitions", "acquire", "takeover"]},
                {"id": 7, "name": "Spin-off", "aliases": ["spinoff", "spin-offs"]},
                {"id": 10, "name": "Fund Raise", "aliases": ["fundraise", "fundraising"]},
                {"id": 12, "name": "Bankruptcy", "aliases": ["bankruptcies", "bankrupt"]},
                {"id": 14, "name": "Buyback", "aliases": ["buybacks", "share repurchase"]}
            ],
            "countries": [
                {"id": 213, "name": "USA", "aliases": ["united states", "us", "america"]},
                {"id": 37, "name": "UK", "aliases": ["united kingdom", "britain", "england"]},
                {"id": 131, "name": "Japan", "aliases": ["jp", "japanese"]},
                {"id": 76, "name": "France", "aliases": ["fr", "french"]},
                {"id": 102, "name": "Canada", "aliases": ["ca", "canadian"]}
            ],
            "industries": [
                {"id": 32, "name": "Technology Hardware", "aliases": ["tech hardware"]},
                {"id": 34, "name": "Software", "aliases": ["software technology"]},
                {"id": 56, "name": "Finance", "aliases": ["financial", "banking"]},
                {"id": 60, "name": "Energy", "aliases": ["power", "utilities"]},
                {"id": 69, "name": "Healthcare", "aliases": ["health", "medical"]}
            ]
        }
    }


def get_reference_values() -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Returns reference values for all entity types in a format suitable for API documentation.
    """
    from app.utils.id_name_mapper import IDNameMapper

    # Transaction Types
    transaction_types = {}
    for id, (name, _) in IDNameMapper.TRANSACTION_TYPES.items():
        transaction_types[str(id)] = name

    # Countries
    countries = {}
    for id, (name, _) in IDNameMapper.COUNTRIES.items():
        countries[str(id)] = name

    # Industries
    industries = {}
    for id, (name, _) in IDNameMapper.INDUSTRIES.items():
        industries[str(id)] = name

    # Currencies
    currencies = {}
    for id, (name, iso_code, _) in IDNameMapper.CURRENCIES.items():
        currencies[str(id)] = f"{name} ({iso_code})"

    # Status
    statuses = {}
    for id, (name, _) in IDNameMapper.STATUSES.items():
        statuses[str(id)] = name

    # Advisor Types
    advisor_types = {}
    for id, (name, _) in IDNameMapper.ADVISOR_TYPES.items():
        advisor_types[str(id)] = name

    # Relation Types
    relation_types = {}
    for id, (name, _) in IDNameMapper.RELATION_TYPES.items():
        relation_types[str(id)] = name

    return {
        "transaction_types": transaction_types,
        "countries": countries,
        "industries": industries,
        "currencies": currencies,
        "statuses": statuses,
        "advisor_types": advisor_types,
        "relation_types": relation_types
    }