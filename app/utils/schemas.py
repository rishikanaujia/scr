"""Schema constant definitions for database tables."""

class AdvisorTypeSchema:
    """Constants for the ciqAdvisorType table."""
    TABLE = "ciqAdvisorType"
    ALIAS = "at"

    # Primary keys and foreign keys
    ID = "advisortypeid"

    # Status fields
    NAME = "advisortypename"

    # Join condition
    JOIN_CONDITION = "at.advisortypeid = {parent_alias}.{foreign_key}"


class CompanySchema:
    """Constants for the ciqCompany table."""
    TABLE = "ciqCompany"
    ALIAS = "c"

    # Primary keys and foreign keys
    ID = "companyid"

    # Date fields
    YEAR_FOUNDED = "yearfounded"
    MONTH_FOUNDED = "monthfounded"
    DAY_FOUNDED = "dayfounded"

    # Status fields
    COMPANY_TYPE_ID = "companytypeid"
    COMPANY_STATUS_TYPE_ID = "companystatustypeid"

    # ID fields
    SIMPLE_INDUSTRY_ID = "simpleindustryid"
    COUNTRY_ID = "countryid"
    STATE_ID = "stateid"
    INCORPORATION_COUNTRY_ID = "incorporationcountryid"
    INCORPORATION_STATE_ID = "incorporationstateid"

    # Value fields
    OFFICE_PHONE = "officephonevalue"
    OFFICE_FAX = "officefaxvalue"
    OTHER_PHONE = "otherphonevalue"

    # Other fields
    NAME = "companyname"
    CITY = "city"
    ZIP_CODE = "zipcode"
    STREET_ADDRESS1 = "streetaddress1"
    STREET_ADDRESS2 = "streetaddress2"
    STREET_ADDRESS3 = "streetaddress3"
    STREET_ADDRESS4 = "streetaddress4"
    WEBPAGE = "webpage"

    # Join condition
    JOIN_CONDITION = "c.companyid = {parent_alias}.{foreign_key}"


class CompanyRelSchema:
    """Constants for the ciqCompanyRel table."""
    TABLE = "ciqCompanyRel"
    ALIAS = "crel"

    # Primary keys and foreign keys
    ID = "companyrelid"

    # Status fields
    COMPANY_REL_TYPE_ID = "companyreltypeid"
    COMPANY_REL_STAKE_TYPE_ID = "companyrelstaketypeid"

    # ID fields
    COMPANY_ID = "companyid"

    # Other fields
    COMPANY_ID2 = "companyid2"
    PERCENT_OWNERSHIP = "percentownership"
    TOTAL_INVESTMENT = "totalinvestment"

    # Join condition
    JOIN_CONDITION = "crel.companyrelid = {parent_alias}.{foreign_key}"


class CountryGeoSchema:
    """Constants for the ciqCountryGeo table."""
    TABLE = "ciqCountryGeo"
    ALIAS = "geo"

    # Primary keys and foreign keys
    ID = "countryid"

    # ID fields
    REGION_ID = "regionid"

    # Value fields
    COUNTRY = "country"
    ISO_COUNTRY2 = "isocountry2"
    ISO_COUNTRY3 = "isocountry3"

    # Other fields
    REGION = "region"

    # Join condition
    JOIN_CONDITION = "geo.countryid = {parent_alias}.{foreign_key}"


class CurrencySchema:
    """Constants for the ciqCurrency table."""
    TABLE = "ciqCurrency"
    ALIAS = "cur"

    # Primary keys and foreign keys
    ID = "currencyid"

    # ID fields
    COUNTRY_ID = "countryid"

    # Flag fields
    MAJOR_CURRENCY_FLAG = "majorcurrencyflag"

    # Other fields
    NAME = "currencyname"
    ISO_CODE = "isocode"

    # Join condition
    JOIN_CONDITION = "cur.currencyid = {parent_alias}.{foreign_key}"


class SimpleIndustrySchema:
    """Constants for the ciqSimpleIndustry table."""
    TABLE = "ciqSimpleIndustry"
    ALIAS = "si"

    # Primary keys and foreign keys
    ID = "simpleindustryid"

    # Other fields
    DESCRIPTION = "simpleindustrydescription"

    # Join condition
    JOIN_CONDITION = "si.simpleindustryid = {parent_alias}.{foreign_key}"


class TransactionSchema:
    """Constants for the ciqTransaction table."""
    TABLE = "ciqTransaction"
    ALIAS = "tr"

    # Primary keys and foreign keys
    ID = "transactionid"

    # Date fields
    ANNOUNCED_YEAR = "announcedyear"
    ANNOUNCED_MONTH = "announcedmonth"
    ANNOUNCED_DAY = "announcedday"
    CLOSING_YEAR = "closingyear"
    CLOSING_MONTH = "closingmonth"
    CLOSING_DAY = "closingday"

    # Status fields
    TYPE_ID = "transactionidtypeid"
    STATUS_ID = "statusid"

    # ID fields
    COMPANY_ID = "companyid"
    CURRENCY_ID = "currencyid"

    # Value fields
    TRANSACTION_SIZE = "transactionsize"

    # Other fields
    COMMENTS = "comments"
    ROUND_NUMBER = "roundnumber"

    # Join condition
    JOIN_CONDITION = "tr.transactionid = {parent_alias}.{foreign_key}"


class TransactionToAdvisorSchema:
    """Constants for the ciqTransactionToAdvisor table."""
    TABLE = "ciqTransactionToAdvisor"
    ALIAS = "adv"

    # Primary keys and foreign keys
    ID = "transactiontoadvisorid"

    # Status fields
    ADVISORY_TYPE_ID = "advisortypeid"

    # ID fields
    TRANSACTION_ID = "transactionid"
    COMPANY_ID = "companyid"

    # Join condition
    JOIN_CONDITION = "adv.transactiontoadvisorid = {parent_alias}.{foreign_key}"


class TransactionToCompRelTypeSchema:
    """Constants for the ciqTransactionToCompRelType table."""
    TABLE = "ciqTransactionToCompRelType"
    ALIAS = "crt"

    # Primary keys and foreign keys
    ID = "transactiontocompreltypeid"

    # Status fields
    NAME = "transactiontocompanyreltype"

    # Join condition
    JOIN_CONDITION = "crt.transactiontocompreltypeid = {parent_alias}.{foreign_key}"


class TransactionToCompanyRelSchema:
    """Constants for the ciqTransactionToCompanyRel table."""
    TABLE = "ciqTransactionToCompanyRel"
    ALIAS = "cr"

    # Primary keys and foreign keys
    ID = "transactiontocompanyrelid"

    # Status fields
    REL_TYPE_ID = "transactiontocompreltypeid"

    # ID fields
    TRANSACTION_ID = "transactionid"
    COMPANY_REL_ID = "companyrelid"

    # Flag fields
    LEAD_INVESTOR_FLAG = "leadinvestorflag"

    # Other fields
    CURRENT_INVESTMENT = "currentinvestment"
    INDIVIDUAL_EQUITY = "individualequity"
    PERCENT_ACQUIRED = "percentacquired"

    # Join condition
    JOIN_CONDITION = "cr.transactiontocompanyrelid = {parent_alias}.{foreign_key}"


class TransactionTypeSchema:
    """Constants for the ciqTransactionType table."""
    TABLE = "ciqTransactionType"
    ALIAS = "tt"

    # Primary keys and foreign keys
    ID = "transactionidtypeid"

    # Status fields
    NAME = "transactionidtypename"

    # Join condition
    JOIN_CONDITION = "tt.transactionidtypeid = {parent_alias}.{foreign_key}"