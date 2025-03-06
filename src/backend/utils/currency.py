#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Currency utility module for the Freight Price Movement Agent.

This module provides functions for currency conversion and handling,
enabling consistent analysis of freight prices across different currencies
by providing standardized conversion capabilities.
"""

import decimal
from decimal import Decimal
import typing
import datetime
import requests  # version 2.28.x

from ..core.config import settings
from ..core.logging import logger
from ..core.cache import cache_with_ttl
from .api_client import ApiKeyClient
from ..core.exceptions import IntegrationException

# Default currency from settings, fallback to USD if not set
DEFAULT_CURRENCY = settings.DEFAULT_CURRENCY or 'USD'

# Decimal places for currency conversion results
CURRENCY_PRECISION = 4

# Cache exchange rates for 24 hours (in seconds)
EXCHANGE_RATE_CACHE_TTL = 86400


@cache_with_ttl(ttl=EXCHANGE_RATE_CACHE_TTL)
def get_exchange_rate(from_currency: str, to_currency: str, 
                     date: typing.Optional[datetime.date] = None) -> decimal.Decimal:
    """
    Fetches the exchange rate between two currencies.
    
    Args:
        from_currency: Source currency code (3-letter ISO code)
        to_currency: Target currency code (3-letter ISO code)
        date: Optional date for historical rates (defaults to current date)
        
    Returns:
        Exchange rate from source to target currency
        
    Raises:
        IntegrationException: If the exchange rate cannot be fetched
        ValueError: If currency codes are invalid
    """
    # Validate currency codes
    if not is_valid_currency_code(from_currency):
        raise ValueError(f"Invalid source currency code: {from_currency}")
    
    if not is_valid_currency_code(to_currency):
        raise ValueError(f"Invalid target currency code: {to_currency}")
    
    # If the currencies are the same, return 1.0
    if from_currency == to_currency:
        return Decimal('1.0')
    
    # Use current date if none provided
    if date is None:
        date = datetime.date.today()
    
    try:
        # Initialize API client
        api_client = ApiKeyClient(
            base_url=settings.CURRENCY_API_URL,
            api_key=settings.CURRENCY_API_KEY
        )
        
        # Prepare API request parameters
        params = {
            'base': from_currency,
            'symbols': to_currency,
            'date': date.isoformat() if date else 'latest'
        }
        
        # Make API request
        logger.debug(f"Fetching exchange rate from {from_currency} to {to_currency} for date {date}")
        response = api_client.get_json('latest', params=params)
        
        # Extract exchange rate from response
        # Note: This response parsing logic depends on the specific currency API being used
        if 'rates' not in response:
            raise IntegrationException(
                "Unexpected API response format",
                details={
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'date': date.isoformat() if date else None,
                    'response': response
                }
            )
        
        rates = response.get('rates', {})
        if to_currency not in rates:
            raise IntegrationException(
                f"Exchange rate not available for {to_currency}",
                details={
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'date': date.isoformat() if date else None,
                    'available_rates': list(rates.keys())
                }
            )
        
        # Get the rate and convert to Decimal for precision
        rate = Decimal(str(rates[to_currency]))
        
        # Round to specified precision
        rate = rate.quantize(Decimal('0.' + '0' * CURRENCY_PRECISION), 
                            rounding=decimal.ROUND_HALF_UP)
        
        logger.info(f"Exchange rate from {from_currency} to {to_currency} on {date}: {rate}")
        return rate
        
    except Exception as e:
        if isinstance(e, IntegrationException):
            raise
        
        logger.error(f"Error fetching exchange rate: {str(e)}", exc_info=True)
        raise IntegrationException(
            f"Failed to fetch exchange rate from {from_currency} to {to_currency}",
            details={
                'from_currency': from_currency,
                'to_currency': to_currency,
                'date': date.isoformat() if date else None
            },
            original_exception=e
        )


def convert_currency(amount: decimal.Decimal, from_currency: str, to_currency: str,
                   date: typing.Optional[datetime.date] = None) -> decimal.Decimal:
    """
    Converts an amount from one currency to another.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (3-letter ISO code)
        to_currency: Target currency code (3-letter ISO code)
        date: Optional date for historical rates (defaults to current date)
        
    Returns:
        Converted amount in target currency
        
    Raises:
        IntegrationException: If currency conversion fails
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if amount is None:
        raise ValueError("Amount cannot be None")
    
    if not isinstance(amount, Decimal):
        try:
            amount = Decimal(str(amount))
        except (decimal.InvalidOperation, TypeError) as e:
            raise ValueError(f"Invalid amount: {amount}") from e
    
    # Validate currency codes
    if not is_valid_currency_code(from_currency):
        raise ValueError(f"Invalid source currency code: {from_currency}")
    
    if not is_valid_currency_code(to_currency):
        raise ValueError(f"Invalid target currency code: {to_currency}")
    
    # If the currencies are the same, return the amount unchanged
    if from_currency == to_currency:
        return amount
    
    try:
        # Get the exchange rate
        exchange_rate = get_exchange_rate(from_currency, to_currency, date)
        
        # Calculate converted amount
        converted_amount = amount * exchange_rate
        
        # Round to specified precision
        converted_amount = converted_amount.quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION),
            rounding=decimal.ROUND_HALF_UP
        )
        
        logger.debug(f"Converted {amount} {from_currency} to {converted_amount} {to_currency}")
        return converted_amount
        
    except Exception as e:
        logger.error(f"Error converting currency: {str(e)}", exc_info=True)
        raise IntegrationException(
            f"Failed to convert {amount} from {from_currency} to {to_currency}",
            details={
                'amount': str(amount),
                'from_currency': from_currency,
                'to_currency': to_currency,
                'date': date.isoformat() if date else None
            },
            original_exception=e
        )


def normalize_to_default_currency(amount: decimal.Decimal, from_currency: str,
                                date: typing.Optional[datetime.date] = None) -> decimal.Decimal:
    """
    Converts an amount to the system's default currency.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (3-letter ISO code)
        date: Optional date for historical rates (defaults to current date)
        
    Returns:
        Amount converted to default currency
        
    Raises:
        IntegrationException: If currency conversion fails
        ValueError: If inputs are invalid
    """
    try:
        return convert_currency(amount, from_currency, DEFAULT_CURRENCY, date)
    except Exception as e:
        logger.error(f"Error normalizing to default currency: {str(e)}", exc_info=True)
        raise IntegrationException(
            f"Failed to normalize {amount} from {from_currency} to {DEFAULT_CURRENCY}",
            details={
                'amount': str(amount),
                'from_currency': from_currency,
                'to_currency': DEFAULT_CURRENCY,
                'date': date.isoformat() if date else None
            },
            original_exception=e
        )


def format_currency(amount: decimal.Decimal, currency_code: str, 
                   include_symbol: typing.Optional[bool] = True) -> str:
    """
    Formats a currency amount with symbol and proper formatting.
    
    Args:
        amount: Amount to format
        currency_code: Currency code (3-letter ISO code)
        include_symbol: Whether to include currency symbol (default True)
        
    Returns:
        Formatted currency string
        
    Raises:
        ValueError: If inputs are invalid
    """
    if amount is None:
        raise ValueError("Amount cannot be None")
    
    if not is_valid_currency_code(currency_code):
        raise ValueError(f"Invalid currency code: {currency_code}")
    
    try:
        # Convert to Decimal if not already
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        # Round to 2 decimal places for display (standard for currencies)
        formatted_amount = amount.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
        
        # Get currency symbol if requested
        symbol = get_currency_symbol(currency_code) if include_symbol else ""
        
        # Format with thousand separators and decimal point
        amount_str = f"{formatted_amount:,.2f}"
        
        # Combine symbol and amount based on currency convention
        if currency_code in ['JPY', 'KRW']:  # Exceptions where symbol goes after
            formatted_str = f"{amount_str} {symbol}"
        else:
            formatted_str = f"{symbol}{amount_str}"
        
        if not include_symbol:
            formatted_str = amount_str
        
        return formatted_str
        
    except Exception as e:
        logger.error(f"Error formatting currency: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to format {amount} {currency_code}: {str(e)}")


def get_currency_symbol(currency_code: str) -> str:
    """
    Returns the symbol for a given currency code.
    
    Args:
        currency_code: Currency code (3-letter ISO code)
        
    Returns:
        Currency symbol
        
    Raises:
        ValueError: If currency code is invalid
    """
    if not is_valid_currency_code(currency_code):
        raise ValueError(f"Invalid currency code: {currency_code}")
    
    # Common currency symbols
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'CHF',
        'HKD': 'HK$',
        'NZD': 'NZ$',
        'SGD': 'S$',
        'INR': '₹',
        'MXN': 'Mex$',
        'BRL': 'R$',
        'ZAR': 'R',
        'RUB': '₽',
        'KRW': '₩',
        'TRY': '₺',
        'SEK': 'kr',
        'NOK': 'kr',
        'DKK': 'kr',
    }
    
    try:
        # Return the symbol if found, otherwise return the currency code
        return symbols.get(currency_code, currency_code)
    except Exception as e:
        logger.debug(f"Error getting currency symbol for {currency_code}: {str(e)}")
        return currency_code


def is_valid_currency_code(currency_code: str) -> bool:
    """
    Validates if a string is a valid ISO currency code.
    
    Args:
        currency_code: Currency code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not currency_code or not isinstance(currency_code, str):
        return False
    
    # ISO currency codes are always 3 uppercase letters
    if len(currency_code) != 3:
        return False
    
    if not currency_code.isalpha() or not currency_code.isupper():
        return False
    
    # Optionally check against a list of known currency codes
    # This is commented out for now as it would require a comprehensive list
    # known_currencies = ['USD', 'EUR', 'GBP', 'JPY', ...]
    # if currency_code not in known_currencies:
    #     return False
    
    return True


class CurrencyConverter:
    """
    Class for handling currency conversions with caching and batch operations.
    """
    
    def __init__(self, api_key: typing.Optional[str] = None, 
                api_url: typing.Optional[str] = None,
                default_currency: typing.Optional[str] = None):
        """
        Initializes a new CurrencyConverter instance.
        
        Args:
            api_key: Optional API key override
            api_url: Optional API URL override
            default_currency: Optional default currency override
        """
        # Set default currency
        self.default_currency = default_currency or DEFAULT_CURRENCY
        
        # Initialize exchange rates cache
        self._exchange_rates_cache = {}
        
        # Set API credentials
        self._api_key = api_key or settings.CURRENCY_API_KEY
        self._api_url = api_url or settings.CURRENCY_API_URL
        
        # Initialize API client if credentials are provided
        self._api_client = None
        if self._api_key and self._api_url:
            self._api_client = ApiKeyClient(
                base_url=self._api_url,
                api_key=self._api_key
            )
        
        logger.info(f"CurrencyConverter initialized with default currency: {self.default_currency}")
    
    def convert(self, amount: decimal.Decimal, from_currency: str, to_currency: str,
               date: typing.Optional[datetime.date] = None) -> decimal.Decimal:
        """
        Converts an amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (3-letter ISO code)
            to_currency: Target currency code (3-letter ISO code)
            date: Optional date for historical rates (defaults to current date)
            
        Returns:
            Converted amount in target currency
        """
        logger.debug(f"Converting {amount} from {from_currency} to {to_currency}")
        return convert_currency(amount, from_currency, to_currency, date)
    
    def normalize(self, amount: decimal.Decimal, from_currency: str,
                 date: typing.Optional[datetime.date] = None) -> decimal.Decimal:
        """
        Converts an amount to the default currency.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (3-letter ISO code)
            date: Optional date for historical rates (defaults to current date)
            
        Returns:
            Amount in default currency
        """
        logger.debug(f"Normalizing {amount} from {from_currency} to {self.default_currency}")
        return self.convert(amount, from_currency, self.default_currency, date)
    
    def batch_convert(self, amounts_with_currencies: typing.List[typing.Tuple[decimal.Decimal, str]],
                     to_currency: str, date: typing.Optional[datetime.date] = None) -> typing.List[decimal.Decimal]:
        """
        Converts multiple amounts with different currencies to a target currency.
        
        Args:
            amounts_with_currencies: List of (amount, currency) tuples
            to_currency: Target currency code (3-letter ISO code)
            date: Optional date for historical rates (defaults to current date)
            
        Returns:
            List of converted amounts
        """
        logger.debug(f"Batch converting {len(amounts_with_currencies)} amounts to {to_currency}")
        results = []
        
        for amount, currency in amounts_with_currencies:
            converted = self.convert(amount, currency, to_currency, date)
            results.append(converted)
        
        return results
    
    def batch_normalize(self, amounts_with_currencies: typing.List[typing.Tuple[decimal.Decimal, str]],
                       date: typing.Optional[datetime.date] = None) -> typing.List[decimal.Decimal]:
        """
        Converts multiple amounts with different currencies to the default currency.
        
        Args:
            amounts_with_currencies: List of (amount, currency) tuples
            date: Optional date for historical rates (defaults to current date)
            
        Returns:
            List of normalized amounts
        """
        logger.debug(f"Batch normalizing {len(amounts_with_currencies)} amounts to {self.default_currency}")
        return self.batch_convert(amounts_with_currencies, self.default_currency, date)
    
    def get_rate(self, from_currency: str, to_currency: str,
                date: typing.Optional[datetime.date] = None) -> decimal.Decimal:
        """
        Gets the exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code (3-letter ISO code)
            to_currency: Target currency code (3-letter ISO code)
            date: Optional date for historical rates (defaults to current date)
            
        Returns:
            Exchange rate
        """
        logger.debug(f"Getting exchange rate from {from_currency} to {to_currency}")
        return get_exchange_rate(from_currency, to_currency, date)