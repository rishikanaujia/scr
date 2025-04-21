"""Constants for the flexible query builder."""
from enum import IntEnum

# Import schema definitions
from app.utils.schema import (
    AdvisorTypeSchema,
    CompanySchema,
    CompanyRelSchema,
    CountryGeoSchema,
    CurrencySchema,
    SimpleIndustrySchema,
    TransactionSchema,
    TransactionToAdvisorSchema,
    TransactionToCompRelTypeSchema,
    TransactionToCompanyRelSchema,
    TransactionTypeSchema
)

# Table mappings for all database tables
TABLE_MAPPINGS = {
    "advisor_types": AdvisorTypeSchema.TABLE,
    "companies": CompanySchema.TABLE,
    "company_rels": CompanyRelSchema.TABLE,
    "country_geos": CountryGeoSchema.TABLE,
    "currencies": CurrencySchema.TABLE,
    "simple_industries": SimpleIndustrySchema.TABLE,
    "transactions": TransactionSchema.TABLE,
    "transaction_to_advisors": TransactionToAdvisorSchema.TABLE,
    "transaction_to_comp_rel_types": TransactionToCompRelTypeSchema.TABLE,
    "transaction_to_company_rels": TransactionToCompanyRelSchema.TABLE,
    "transaction_types": TransactionTypeSchema.TABLE,
}

# Field mappings for query parameters to database fields
FIELD_MAPPINGS = {
    # Transaction fields
    "transactionId": f"{TransactionSchema.ALIAS}.{TransactionSchema.ID}",
    "type": f"{TransactionSchema.ALIAS}.{TransactionSchema.TYPE_ID}",
    "year": f"{TransactionSchema.ALIAS}.{TransactionSchema.ANNOUNCED_YEAR}",
    "month": f"{TransactionSchema.ALIAS}.{TransactionSchema.ANNOUNCED_MONTH}",
    "day": f"{TransactionSchema.ALIAS}.{TransactionSchema.ANNOUNCED_DAY}",
    "closingYear": f"{TransactionSchema.ALIAS}.{TransactionSchema.CLOSING_YEAR}",
    "closingMonth": f"{TransactionSchema.ALIAS}.{TransactionSchema.CLOSING_MONTH}",
    "closingDay": f"{TransactionSchema.ALIAS}.{TransactionSchema.CLOSING_DAY}",
    "size": f"{TransactionSchema.ALIAS}.{TransactionSchema.TRANSACTION_SIZE}",
    "currencyId": f"{TransactionSchema.ALIAS}.{TransactionSchema.CURRENCY_ID}",
    "statusId": f"{TransactionSchema.ALIAS}.{TransactionSchema.STATUS_ID}",
    "comments": f"{TransactionSchema.ALIAS}.{TransactionSchema.COMMENTS}",
    "roundNumber": f"{TransactionSchema.ALIAS}.{TransactionSchema.ROUND_NUMBER}",

    # Transaction type fields
    "transactionType": f"{TransactionTypeSchema.ALIAS}.{TransactionTypeSchema.ID}",
    "typeName": f"{TransactionTypeSchema.ALIAS}.{TransactionTypeSchema.NAME}",

    # Company fields
    "companyId": f"{CompanySchema.ALIAS}.{CompanySchema.ID}",
    "companyName": f"{CompanySchema.ALIAS}.{CompanySchema.NAME}",
    "industry": f"{CompanySchema.ALIAS}.{CompanySchema.SIMPLE_INDUSTRY_ID}",
    "country": f"{CompanySchema.ALIAS}.{CompanySchema.COUNTRY_ID}",
    "state": f"{CompanySchema.ALIAS}.{CompanySchema.STATE_ID}",
    "city": f"{CompanySchema.ALIAS}.{CompanySchema.CITY}",
    "zipCode": f"{CompanySchema.ALIAS}.{CompanySchema.ZIP_CODE}",
    "companyType": f"{CompanySchema.ALIAS}.{CompanySchema.COMPANY_TYPE_ID}",
    "companyStatus": f"{CompanySchema.ALIAS}.{CompanySchema.COMPANY_STATUS_TYPE_ID}",
    "yearFounded": f"{CompanySchema.ALIAS}.{CompanySchema.YEAR_FOUNDED}",
    "monthFounded": f"{CompanySchema.ALIAS}.{CompanySchema.MONTH_FOUNDED}",
    "dayFounded": f"{CompanySchema.ALIAS}.{CompanySchema.DAY_FOUNDED}",
    "incorporationCountry": f"{CompanySchema.ALIAS}.{CompanySchema.INCORPORATION_COUNTRY_ID}",
    "incorporationState": f"{CompanySchema.ALIAS}.{CompanySchema.INCORPORATION_STATE_ID}",
    "officePhone": f"{CompanySchema.ALIAS}.{CompanySchema.OFFICE_PHONE}",
    "officeFax": f"{CompanySchema.ALIAS}.{CompanySchema.OFFICE_FAX}",
    "otherPhone": f"{CompanySchema.ALIAS}.{CompanySchema.OTHER_PHONE}",
    "webpage": f"{CompanySchema.ALIAS}.{CompanySchema.WEBPAGE}",

    # Simple industry fields
    "industryDescription": f"{SimpleIndustrySchema.ALIAS}.{SimpleIndustrySchema.DESCRIPTION}",

    # Country fields
    "countryName": f"{CountryGeoSchema.ALIAS}.{CountryGeoSchema.COUNTRY}",
    "isoCountry2": f"{CountryGeoSchema.ALIAS}.{CountryGeoSchema.ISO_COUNTRY2}",
    "isoCountry3": f"{CountryGeoSchema.ALIAS}.{CountryGeoSchema.ISO_COUNTRY3}",
    "region": f"{CountryGeoSchema.ALIAS}.{CountryGeoSchema.REGION}",
    "regionId": f"{CountryGeoSchema.ALIAS}.{CountryGeoSchema.REGION_ID}",

    # Currency fields
    "currencyName": f"{CurrencySchema.ALIAS}.{CurrencySchema.NAME}",
    "isoCode": f"{CurrencySchema.ALIAS}.{CurrencySchema.ISO_CODE}",
    "majorCurrency": f"{CurrencySchema.ALIAS}.{CurrencySchema.MAJOR_CURRENCY_FLAG}",

    # Transaction to company relationship fields
    "relationshipType": f"{TransactionToCompRelTypeSchema.ALIAS}.{TransactionToCompRelTypeSchema.ID}",
    "relationshipName": f"{TransactionToCompRelTypeSchema.ALIAS}.{TransactionToCompRelTypeSchema.NAME}",
    "currentInvestment": f"{TransactionToCompanyRelSchema.ALIAS}.{TransactionToCompanyRelSchema.CURRENT_INVESTMENT}",
    "individualEquity": f"{TransactionToCompanyRelSchema.ALIAS}.{TransactionToCompanyRelSchema.INDIVIDUAL_EQUITY}",
    "percentAcquired": f"{TransactionToCompanyRelSchema.ALIAS}.{TransactionToCompanyRelSchema.PERCENT_ACQUIRED}",
    "leadInvestor": f"{TransactionToCompanyRelSchema.ALIAS}.{TransactionToCompanyRelSchema.LEAD_INVESTOR_FLAG}",

    # Company relationship fields
    "companyRelId": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.ID}",
    "companyId2": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.COMPANY_ID2}",
    "companyRelType": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.COMPANY_REL_TYPE_ID}",
    "companyRelStakeType": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.COMPANY_REL_STAKE_TYPE_ID}",
    "percentOwnership": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.PERCENT_OWNERSHIP}",
    "totalInvestment": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.TOTAL_INVESTMENT}",

    # Advisor fields
    "advisorType": f"{AdvisorTypeSchema.ALIAS}.{AdvisorTypeSchema.ID}",
    "advisorTypeName": f"{AdvisorTypeSchema.ALIAS}.{AdvisorTypeSchema.NAME}",
    "advisorId": f"{TransactionToAdvisorSchema.ALIAS}.{TransactionToAdvisorSchema.COMPANY_ID}",

    # Special aggregation fields
    "count": "COUNT(*)",
    "total": "SUM(tr.transactionsize)",
    "average": "AVG(tr.transactionsize)",
    "max": "MAX(tr.transactionsize)",
    "min": "MIN(tr.transactionsize)"
}

# Join paths for tables
JOIN_PATHS = {
    "type": {
        "table": TransactionTypeSchema.TABLE,
        "alias": TransactionTypeSchema.ALIAS,
        "condition": f"{TransactionSchema.ALIAS}.{TransactionSchema.TYPE_ID} = {TransactionTypeSchema.ALIAS}.{TransactionTypeSchema.ID}"
    },
    "company": {
        "table": CompanySchema.TABLE,
        "alias": CompanySchema.ALIAS,
        "condition": f"{TransactionSchema.ALIAS}.{TransactionSchema.COMPANY_ID} = {CompanySchema.ALIAS}.{CompanySchema.ID}"
    },
    "industry": {
        "table": SimpleIndustrySchema.TABLE,
        "alias": SimpleIndustrySchema.ALIAS,
        "condition": f"{CompanySchema.ALIAS}.{CompanySchema.SIMPLE_INDUSTRY_ID} = {SimpleIndustrySchema.ALIAS}.{SimpleIndustrySchema.ID}",
        "requires": ["company"]
    },
    "country": {
        "table": CountryGeoSchema.TABLE,
        "alias": CountryGeoSchema.ALIAS,
        "condition": f"{CompanySchema.ALIAS}.{CompanySchema.COUNTRY_ID} = {CountryGeoSchema.ALIAS}.{CountryGeoSchema.ID}",
        "requires": ["company"]
    },
    "currency": {
        "table": CurrencySchema.TABLE,
        "alias": CurrencySchema.ALIAS,
        "condition": f"{TransactionSchema.ALIAS}.{TransactionSchema.CURRENCY_ID} = {CurrencySchema.ALIAS}.{CurrencySchema.ID}"
    },
    "transaction_rel": {
        "table": TransactionToCompanyRelSchema.TABLE,
        "alias": TransactionToCompanyRelSchema.ALIAS,
        "condition": f"{TransactionToCompanyRelSchema.ALIAS}.{TransactionToCompanyRelSchema.TRANSACTION_ID} = {TransactionSchema.ALIAS}.{TransactionSchema.ID}"
    },
    "relation_type": {
        "table": TransactionToCompRelTypeSchema.TABLE,
        "alias": TransactionToCompRelTypeSchema.ALIAS,
        "condition": f"{TransactionToCompanyRelSchema.ALIAS}.{TransactionToCompanyRelSchema.REL_TYPE_ID} = {TransactionToCompRelTypeSchema.ALIAS}.{TransactionToCompRelTypeSchema.ID}",
        "requires": ["transaction_rel"]
    },
    "company_rel": {
        "table": CompanyRelSchema.TABLE,
        "alias": CompanyRelSchema.ALIAS,
        "condition": f"{TransactionToCompanyRelSchema.ALIAS}.{TransactionToCompanyRelSchema.COMPANY_REL_ID} = {CompanyRelSchema.ALIAS}.{CompanyRelSchema.ID}",
        "requires": ["transaction_rel"]
    },
    "buyer_company": {
        "table": CompanySchema.TABLE,
        "alias": "buyer",
        "condition": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.COMPANY_ID} = buyer.{CompanySchema.ID}",
        "requires": ["company_rel"]
    },
    "buyer_industry": {
        "table": SimpleIndustrySchema.TABLE,
        "alias": "buyersi",
        "condition": f"buyer.{CompanySchema.SIMPLE_INDUSTRY_ID} = buyersi.{SimpleIndustrySchema.ID}",
        "requires": ["buyer_company"]
    },
    "buyer_country": {
        "table": CountryGeoSchema.TABLE,
        "alias": "buyergeo",
        "condition": f"buyer.{CompanySchema.COUNTRY_ID} = buyergeo.{CountryGeoSchema.ID}",
        "requires": ["buyer_company"]
    },
    "target_company": {
        "table": CompanySchema.TABLE,
        "alias": "target",
        "condition": f"{CompanyRelSchema.ALIAS}.{CompanyRelSchema.COMPANY_ID2} = target.{CompanySchema.ID}",
        "requires": ["company_rel"]
    },
    "target_industry": {
        "table": SimpleIndustrySchema.TABLE,
        "alias": "targetsi",
        "condition": f"target.{CompanySchema.SIMPLE_INDUSTRY_ID} = targetsi.{SimpleIndustrySchema.ID}",
        "requires": ["target_company"]
    },
    "target_country": {
        "table": CountryGeoSchema.TABLE,
        "alias": "targetgeo",
        "condition": f"target.{CompanySchema.COUNTRY_ID} = targetgeo.{CountryGeoSchema.ID}",
        "requires": ["target_company"]
    },
    "advisory_type": {
        "table": AdvisorTypeSchema.TABLE,
        "alias": AdvisorTypeSchema.ALIAS,
        "condition": f"{TransactionToAdvisorSchema.ALIAS}.{TransactionToAdvisorSchema.ADVISORY_TYPE_ID} = {AdvisorTypeSchema.ALIAS}.{AdvisorTypeSchema.ID}",
        "requires": ["advisor_rel"]
    },
    "advisor_rel": {
        "table": TransactionToAdvisorSchema.TABLE,
        "alias": TransactionToAdvisorSchema.ALIAS,
        "condition": f"{TransactionToAdvisorSchema.ALIAS}.{TransactionToAdvisorSchema.TRANSACTION_ID} = {TransactionSchema.ALIAS}.{TransactionSchema.ID}"
    },
    "advisor_company": {
        "table": CompanySchema.TABLE,
        "alias": "advcompany",
        "condition": f"{TransactionToAdvisorSchema.ALIAS}.{TransactionToAdvisorSchema.COMPANY_ID} = advcompany.{CompanySchema.ID}",
        "requires": ["advisor_rel"]
    },
    "currency_country": {
        "table": CountryGeoSchema.TABLE,
        "alias": "curgeo",
        "condition": f"{CurrencySchema.ALIAS}.{CurrencySchema.COUNTRY_ID} = curgeo.{CountryGeoSchema.ID}",
        "requires": ["currency"]
    }
}

# Supported filter operators
FILTER_OPERATORS = {
    "eq": "=",
    "gte": ">=",
    "lte": "<=",
    "gt": ">",
    "lt": "<",
    "ne": "!=",
    "like": "LIKE",
    "ilike": "ILIKE",
    "null": "IS NULL",
    "notnull": "IS NOT NULL",
    "between": "BETWEEN",
    "starts": "LIKE",
    "ends": "LIKE",
    "contains": "LIKE"
}

# Special SQL functions
SQL_FUNCTIONS = {
    "distinct": "DISTINCT({})",
    "count": "COUNT({})",
    "count_distinct": "COUNT(DISTINCT({}))",
    "sum": "SUM({})",
    "avg": "AVG({})",
    "min": "MIN({})",
    "max": "MAX({})",

    # Window functions
    "row_number": "ROW_NUMBER() OVER (PARTITION BY {} ORDER BY {})",
    "rank": "RANK() OVER (PARTITION BY {} ORDER BY {})",
    "dense_rank": "DENSE_RANK() OVER (PARTITION BY {} ORDER BY {})",

    # Date functions
    "year": "EXTRACT(YEAR FROM {})",
    "quarter": "EXTRACT(QUARTER FROM {})",
    "month": "EXTRACT(MONTH FROM {})",
    "day": "EXTRACT(DAY FROM {})",

    # String functions
    "concat": "CONCAT({}, {})",
    "upper": "UPPER({})",
    "lower": "LOWER({})",
    "trim": "TRIM({})",

    # Conditional functions
    "case_when": "CASE WHEN {} THEN {} ELSE {} END",
    "coalesce": "COALESCE({}, {})"
}

# Security patterns to prevent SQL injection
SECURITY_PATTERNS = {
    "sql_injection": [
        r";\s*SELECT", r";\s*INSERT", r";\s*UPDATE", r";\s*DELETE", r";\s*DROP",
        r"UNION\s+SELECT", r"--", r"/\*", r"\*/", r"xp_cmdshell", r"exec\s+master"
    ],
    "safe_field_pattern": r"^[a-zA-Z][a-zA-Z0-9_\.]*$",
    "safe_alias_pattern": r"^[a-zA-Z][a-zA-Z0-9_]*$",
    "safe_value_pattern": r"^[^;\"'\\]*$"
}


# Transaction Type enum values
class TransactionType(IntEnum):
    """Constants for transaction types from ciqTransactionType."""
    ACQUISITION = 1
    MERGER = 2
    MINORITY_STAKE = 3
    JOINT_VENTURE = 4
    PRIVATE_PLACEMENT = 5
    VENTURE_CAPITAL = 6
    PRIVATE_EQUITY = 7
    SPIN_OFF = 8
    DIVESTITURE = 9
    FUND_RAISE = 10
    SHARE_REPURCHASE = 11
    BANKRUPTCY = 12
    DEBT_OFFERING = 13
    BUYBACK = 14
    RESTRUCTURING = 15
    IPO = 16


# Transaction Status enum values
class TransactionStatus(IntEnum):
    """Constants for transaction status."""
    ANNOUNCED = 1
    PENDING = 2
    COMPLETED = 3
    TERMINATED = 4
    WITHDRAWN = 5
    EXPIRED = 6


# Relationship Type enum values
class RelationshipType(IntEnum):
    """Constants for transaction-company relationship types."""
    ACQUIRER = 1
    TARGET = 2
    SELLER = 3
    INVESTOR = 4
    ISSUER = 5


# Advisor Type enum values
class AdvisorType(IntEnum):
    """Constants for advisor types."""
    FINANCIAL = 1
    LEGAL = 2
    ACCOUNTING = 3
    STRATEGIC = 4