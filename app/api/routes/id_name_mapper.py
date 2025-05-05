"""
ID-Name Mapper Module for Transaction API

This module provides mapping between human-readable names and numeric IDs
for various entities in the transaction system.
"""
from typing import Dict, List, Union, Optional, Tuple
import re


class IDNameMapper:
    """
    Provides bidirectional mapping between numeric IDs and human-readable names
    for transaction types, countries, industries, currencies, etc.
    """

    # Transaction Types mapping
    TRANSACTION_TYPES = {
        # ID: (name, [aliases])
        1: ("M&A", ["m&a", "m and a", "merger and acquisition", "merger"]),
        2: ("Acquisition", ["acquisitions", "acquire", "takeover"]),
        7: ("Spin-off", ["spin off", "spinoff", "spin-offs", "spinoffs"]),
        10: ("Fund Raise", ["fundraise", "fundraising", "funding", "investment"]),
        12: ("Bankruptcy", ["bankruptcies", "bankrupt", "insolvency"]),
        14: ("Buyback", ["buybacks", "share repurchase", "stock repurchase"]),
    }

    # Countries mapping
    COUNTRIES = {
        # ID: (name, [aliases])
        213: ("USA", ["united states", "us", "america", "united states of america"]),
        37: ("UK", ["united kingdom", "britain", "great britain", "england"]),
        131: ("Japan", ["jp", "japanese"]),
        147: ("Germany", ["de", "german", "deutschland"]),
        76: ("France", ["fr", "french"]),
        102: ("Canada", ["ca", "canadian"]),
        7: ("Australia", ["au", "aus", "australian"]),
        16: ("Brazil", ["br", "brazilian"]),
        99: ("India", ["in", "indian"]),
        30: ("China", ["cn", "chinese"]),
    }

    # Industries mapping
    INDUSTRIES = {
        # ID: (name, [aliases])
        32: ("Technology Hardware", ["tech hardware", "hardware technology"]),
        34: ("Software", ["software technology", "tech software"]),
        56: ("Finance", ["financial", "banking", "financial services"]),
        60: ("Energy", ["power", "utilities", "oil and gas"]),
        69: ("Healthcare", ["health", "medical", "biotech", "pharmaceutical"]),
        41: ("Manufacturing", ["industrial", "production"]),
        23: ("Retail", ["shops", "ecommerce", "e-commerce"]),
        35: ("Automotive", ["auto", "cars", "vehicles"]),
        55: ("Telecommunications", ["telecom", "communications"]),
        58: ("Technology", ["tech", "information technology", "it"]),
        61: ("Internet", ["web", "online"]),
        62: ("Media", ["entertainment", "publishing"]),
        63: ("Real Estate", ["property", "realty"]),
        64: ("Consumer", ["consumer goods", "consumer products"]),
        6: ("Agriculture", ["farming", "agribusiness"]),
        2: ("Aerospace", ["aviation", "defense"]),
        50: ("Transportation", ["logistics", "shipping"]),
    }

    # Currencies mapping
    CURRENCIES = {
        # ID: (name, iso_code, [aliases])
        50: ("US Dollar", "USD", ["dollar", "dollars", "usd", "$"]),
        49: ("Euro", "EUR", ["eur", "€"]),
        22: ("British Pound", "GBP", ["pound", "pounds", "sterling", "gbp", "£"]),
        63: ("Japanese Yen", "JPY", ["yen", "jpy", "¥"]),
        26: ("Canadian Dollar", "CAD", ["cad", "c$"]),
        25: ("Australian Dollar", "AUD", ["aud", "a$"]),
        160: ("Other Currency", "", ["other"]),
    }

    # Status mapping
    STATUSES = {
        # ID: (name, [aliases])
        2: ("Completed", ["complete", "finished", "done"]),
        1: ("Pending", ["in progress", "ongoing", "active"]),
        3: ("Cancelled", ["canceled", "abandoned", "terminated"]),
    }

    # Advisor Types mapping
    ADVISOR_TYPES = {
        # ID: (name, [aliases])
        2: ("Legal", ["law", "legal advisor", "legal counsel"]),
        1: ("Financial", ["finance", "banking advisor", "investment banker"]),
        3: ("Consulting", ["consultant", "management consultant"]),
    }

    # Relation Types mapping
    RELATION_TYPES = {
        # ID: (name, [aliases])
        1: ("Buyer-Target", ["buyer", "acquirer"]),
        2: ("Seller", ["selling", "divesting"]),
    }

    # Reverse mappings
    _transaction_types_reverse = {}
    _countries_reverse = {}
    _industries_reverse = {}
    _currencies_reverse = {}
    _statuses_reverse = {}
    _advisor_types_reverse = {}
    _relation_types_reverse = {}
    _currency_iso_codes = {}

    @classmethod
    def build_reverse_maps(cls):
        """Build reverse maps (name->id) for all categories"""
        # Build transaction types reverse map
        for id, (name, aliases) in cls.TRANSACTION_TYPES.items():
            cls._transaction_types_reverse[name.lower()] = id
            for alias in aliases:
                cls._transaction_types_reverse[alias.lower()] = id

        # Build countries reverse map
        for id, (name, aliases) in cls.COUNTRIES.items():
            cls._countries_reverse[name.lower()] = id
            for alias in aliases:
                cls._countries_reverse[alias.lower()] = id

        # Build industries reverse map
        for id, (name, aliases) in cls.INDUSTRIES.items():
            cls._industries_reverse[name.lower()] = id
            for alias in aliases:
                cls._industries_reverse[alias.lower()] = id

        # Build currencies reverse map
        for id, (name, iso_code, aliases) in cls.CURRENCIES.items():
            cls._currencies_reverse[name.lower()] = id
            cls._currency_iso_codes[iso_code.upper()] = id
            for alias in aliases:
                cls._currencies_reverse[alias.lower()] = id

        # Build statuses reverse map
        for id, (name, aliases) in cls.STATUSES.items():
            cls._statuses_reverse[name.lower()] = id
            for alias in aliases:
                cls._statuses_reverse[alias.lower()] = id

        # Build advisor types reverse map
        for id, (name, aliases) in cls.ADVISOR_TYPES.items():
            cls._advisor_types_reverse[name.lower()] = id
            for alias in aliases:
                cls._advisor_types_reverse[alias.lower()] = id

        # Build relation types reverse map
        for id, (name, aliases) in cls.RELATION_TYPES.items():
            cls._relation_types_reverse[name.lower()] = id
            for alias in aliases:
                cls._relation_types_reverse[alias.lower()] = id

    @classmethod
    def get_transaction_type_id(cls, type_name: str) -> Optional[int]:
        """Convert transaction type name to ID"""
        return cls._transaction_types_reverse.get(type_name.lower())

    @classmethod
    def get_transaction_type_name(cls, type_id: int) -> Optional[str]:
        """Convert transaction type ID to name"""
        if type_id in cls.TRANSACTION_TYPES:
            return cls.TRANSACTION_TYPES[type_id][0]
        return None

    @classmethod
    def get_country_id(cls, country_name: str) -> Optional[int]:
        """Convert country name to ID"""
        return cls._countries_reverse.get(country_name.lower())

    @classmethod
    def get_country_name(cls, country_id: int) -> Optional[str]:
        """Convert country ID to name"""
        if country_id in cls.COUNTRIES:
            return cls.COUNTRIES[country_id][0]
        return None

    @classmethod
    def get_industry_id(cls, industry_name: str) -> Optional[int]:
        """Convert industry name to ID"""
        return cls._industries_reverse.get(industry_name.lower())

    @classmethod
    def get_industry_name(cls, industry_id: int) -> Optional[str]:
        """Convert industry ID to name"""
        if industry_id in cls.INDUSTRIES:
            return cls.INDUSTRIES[industry_id][0]
        return None

    @classmethod
    def get_currency_id(cls, currency_name_or_code: str) -> Optional[int]:
        """Convert currency name or ISO code to ID"""
        # Check if it's an ISO code first
        currency_id = cls._currency_iso_codes.get(currency_name_or_code.upper())
        if currency_id:
            return currency_id

        # Otherwise, check regular names/aliases
        return cls._currencies_reverse.get(currency_name_or_code.lower())

    @classmethod
    def get_currency_name(cls, currency_id: int) -> Optional[str]:
        """Convert currency ID to name"""
        if currency_id in cls.CURRENCIES:
            return cls.CURRENCIES[currency_id][0]
        return None

    @classmethod
    def get_currency_iso_code(cls, currency_id: int) -> Optional[str]:
        """Convert currency ID to ISO code"""
        if currency_id in cls.CURRENCIES:
            return cls.CURRENCIES[currency_id][1]
        return None

    @classmethod
    def get_status_id(cls, status_name: str) -> Optional[int]:
        """Convert status name to ID"""
        return cls._statuses_reverse.get(status_name.lower())

    @classmethod
    def get_status_name(cls, status_id: int) -> Optional[str]:
        """Convert status ID to name"""
        if status_id in cls.STATUSES:
            return cls.STATUSES[status_id][0]
        return None

    @classmethod
    def get_advisor_type_id(cls, advisor_type_name: str) -> Optional[int]:
        """Convert advisor type name to ID"""
        return cls._advisor_types_reverse.get(advisor_type_name.lower())

    @classmethod
    def get_advisor_type_name(cls, advisor_type_id: int) -> Optional[str]:
        """Convert advisor type ID to name"""
        if advisor_type_id in cls.ADVISOR_TYPES:
            return cls.ADVISOR_TYPES[advisor_type_id][0]
        return None

    @classmethod
    def get_relation_type_id(cls, relation_type_name: str) -> Optional[int]:
        """Convert relation type name to ID"""
        return cls._relation_types_reverse.get(relation_type_name.lower())

    @classmethod
    def get_relation_type_name(cls, relation_type_id: int) -> Optional[str]:
        """Convert relation type ID to name"""
        if relation_type_id in cls.RELATION_TYPES:
            return cls.RELATION_TYPES[relation_type_id][0]
        return None

    @classmethod
    def convert_multi_value_param(cls, param_value: str, converter_func) -> str:
        """
        Handles conversion of multi-value parameters (comma-separated lists)
        and parameters with operators (gte:, lte:, etc.)

        Args:
            param_value: The parameter value to convert (e.g., "USA,UK" or "gte:Finance")
            converter_func: Function to convert a single value

        Returns:
            Converted parameter value with IDs (e.g., "213,37" or "gte:56")
        """
        # Handle null/notnull operators
        if param_value in ('null:', 'notnull:'):
            return param_value

        # Process operators like gte:, lte:, between:, etc.
        match = re.match(r'^(gte:|lte:|gt:|lt:|ne:|like:|between:)(.+)$', param_value)
        if match:
            operator, value = match.groups()

            # Handle between operator (e.g., between:2018,2021)
            if operator == 'between:' and ',' in value:
                parts = value.split(',')
                converted_parts = []
                for part in parts:
                    converted = converter_func(part.strip())
                    converted_parts.append(str(converted) if converted is not None else part.strip())
                return f"{operator}{','.join(converted_parts)}"

            # Handle other operators
            converted = converter_func(value)
            return f"{operator}{converted if converted is not None else value}"

        # Handle comma-separated lists
        if ',' in param_value:
            parts = param_value.split(',')
            converted_parts = []
            for part in parts:
                converted = converter_func(part.strip())
                converted_parts.append(str(converted) if converted is not None else part.strip())
            return ','.join(converted_parts)

        # Single value
        converted = converter_func(param_value)
        return str(converted) if converted is not None else param_value


# Initialize the reverse maps
IDNameMapper.build_reverse_maps()


# Module-level functions for easy access
def convert_param(param_name: str, param_value: str) -> str:
    """
    Convert a parameter value from name to ID based on parameter name

    Args:
        param_name: The name of the parameter (e.g., "type", "country")
        param_value: The parameter value to convert (can be name or ID)

    Returns:
        Parameter value converted to ID if it was a name, or original value if already an ID
    """
    if param_value is None:
        return None

    # If it's already a numeric ID, return as is
    if param_value.isdigit() or (param_value.startswith('-') and param_value[1:].isdigit()):
        return param_value

    # Check operators and multiple values
    has_operator = any(
        op in param_value for op in ['gte:', 'lte:', 'gt:', 'lt:', 'ne:', 'like:', 'between:', 'null:', 'notnull:'])
    has_multiple = ',' in param_value

    if not has_operator and not has_multiple:
        # Try direct conversion if it's a simple value
        if param_name in ['type', 'transactionIdType']:
            type_id = IDNameMapper.get_transaction_type_id(param_value)
            return str(type_id) if type_id is not None else param_value

        elif param_name in ['country', 'buyerCountry', 'targetCountry']:
            country_id = IDNameMapper.get_country_id(param_value)
            return str(country_id) if country_id is not None else param_value

        elif param_name in ['industry', 'buyerIndustry', 'targetIndustry']:
            industry_id = IDNameMapper.get_industry_id(param_value)
            return str(industry_id) if industry_id is not None else param_value

        elif param_name in ['currencyId', 'currency']:
            currency_id = IDNameMapper.get_currency_id(param_value)
            return str(currency_id) if currency_id is not None else param_value

        elif param_name == 'statusId':
            status_id = IDNameMapper.get_status_id(param_value)
            return str(status_id) if status_id is not None else param_value

        elif param_name == 'advisorTypeId':
            advisor_type_id = IDNameMapper.get_advisor_type_id(param_value)
            return str(advisor_type_id) if advisor_type_id is not None else param_value

        elif param_name == 'relationType':
            relation_type_id = IDNameMapper.get_relation_type_id(param_value)
            return str(relation_type_id) if relation_type_id is not None else param_value

    # Handle complex parameters with operators or multiple values
    if param_name in ['type', 'transactionIdType']:
        return IDNameMapper.convert_multi_value_param(param_value, IDNameMapper.get_transaction_type_id)

    elif param_name in ['country', 'buyerCountry', 'targetCountry']:
        return IDNameMapper.convert_multi_value_param(param_value, IDNameMapper.get_country_id)

    elif param_name in ['industry', 'buyerIndustry', 'targetIndustry']:
        return IDNameMapper.convert_multi_value_param(param_value, IDNameMapper.get_industry_id)

    elif param_name in ['currencyId', 'currency']:
        return IDNameMapper.convert_multi_value_param(param_value, IDNameMapper.get_currency_id)

    elif param_name == 'statusId':
        return IDNameMapper.convert_multi_value_param(param_value, IDNameMapper.get_status_id)

    elif param_name == 'advisorTypeId':
        return IDNameMapper.convert_multi_value_param(param_value, IDNameMapper.get_advisor_type_id)

    elif param_name == 'relationType':
        return IDNameMapper.convert_multi_value_param(param_value, IDNameMapper.get_relation_type_id)

    # Return original value if no conversion applied
    return param_value