#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility module providing formatting functions for various data types in the Freight Price Movement Agent.

This module handles the consistent formatting of currency values, percentages, trend indicators, 
dates, and JSON values to ensure standardized presentation across the application.
"""

import decimal
from decimal import Decimal
import typing
import datetime
import json

from ..models.enums import TrendDirection, GranularityType
from .currency import get_currency_symbol
from ..core.logging import logger

# Decimal places for display formatting
DISPLAY_PRECISION = 2  # Decimal places for display formatting

# Symbols for trend direction visualization
TREND_SYMBOLS = {
    TrendDirection.INCREASING: '↑',
    TrendDirection.DECREASING: '↓',
    TrendDirection.STABLE: '→'
}  # Symbols for trend direction visualization

# Standard date format for display
DATE_FORMAT = '%Y-%m-%d'  # Standard date format for display

# Human-readable labels for granularity types
GRANULARITY_LABELS = {
    GranularityType.DAILY: 'Daily',
    GranularityType.WEEKLY: 'Weekly',
    GranularityType.MONTHLY: 'Monthly',
    GranularityType.QUARTERLY: 'Quarterly',
    GranularityType.CUSTOM: 'Custom'
}  # Human-readable labels for granularity types


def format_currency(amount: decimal.Decimal, currency_code: str, 
                   include_symbol: typing.Optional[bool] = True) -> str:
    """
    Formats a currency amount with symbol and proper formatting.
    
    Args:
        amount: Amount to format
        currency_code: Currency code (e.g., USD, EUR)
        include_symbol: Whether to include the currency symbol (default True)
        
    Returns:
        Formatted currency string
    """
    try:
        if amount is None:
            logger.debug("Attempted to format None as currency")
            return ''
        
        # Ensure amount is a Decimal for consistent formatting
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        # Round to display precision
        rounded_amount = amount.quantize(
            Decimal('0.' + '0' * DISPLAY_PRECISION),
            rounding=decimal.ROUND_HALF_UP
        )
        
        # Format with thousand separators and fixed decimal places
        formatted_amount = f"{rounded_amount:,.{DISPLAY_PRECISION}f}"
        
        # Add currency symbol if requested
        if include_symbol:
            symbol = get_currency_symbol(currency_code)
            
            # Most currencies show symbol before amount, but some exceptions exist
            if currency_code in ['JPY', 'KRW']:
                return f"{formatted_amount} {symbol}"
            else:
                return f"{symbol}{formatted_amount}"
        else:
            return formatted_amount
    
    except Exception as e:
        logger.error(f"Error formatting currency: {e}")
        # Return a basic formatted string as fallback
        try:
            return f"{amount:.{DISPLAY_PRECISION}f}" if amount is not None else ''
        except:
            return str(amount) if amount is not None else ''


def format_percentage(value: decimal.Decimal, 
                     precision: typing.Optional[int] = None,
                     include_sign: typing.Optional[bool] = True) -> str:
    """
    Formats a decimal value as a percentage with sign.
    
    Args:
        value: Value to format as percentage
        precision: Number of decimal places (default: DISPLAY_PRECISION)
        include_sign: Whether to include + sign for positive values (default True)
        
    Returns:
        Formatted percentage string
    """
    try:
        if value is None:
            logger.debug("Attempted to format None as percentage")
            return ''
        
        # Use default precision if not specified
        if precision is None:
            precision = DISPLAY_PRECISION
        
        # Convert to percentage value (multiply by 100)
        percentage_value = value * 100
        
        # Round to specified precision
        rounded_value = percentage_value.quantize(
            Decimal('0.' + '0' * precision),
            rounding=decimal.ROUND_HALF_UP
        )
        
        # Format with fixed decimal places
        formatted_value = f"{abs(rounded_value):.{precision}f}"
        
        # Add sign
        if include_sign:
            if value > 0:
                return f"+{formatted_value}%"
            elif value < 0:
                return f"-{formatted_value}%"
            else:
                return f"{formatted_value}%"
        else:
            if value < 0:
                return f"-{formatted_value}%"
            else:
                return f"{formatted_value}%"
    
    except Exception as e:
        logger.error(f"Error formatting percentage: {e}")
        # Return a basic formatted string as fallback
        try:
            percentage = value * 100 if value is not None else 0
            return f"{percentage:.{precision or DISPLAY_PRECISION}f}%" 
        except:
            return f"{value}%" if value is not None else ''


def format_trend(trend: TrendDirection, 
                include_symbol: typing.Optional[bool] = True) -> str:
    """
    Formats a trend direction with appropriate symbol.
    
    Args:
        trend: Trend direction enum value
        include_symbol: Whether to include trend symbol (default True)
        
    Returns:
        Formatted trend string
    """
    try:
        if trend is None:
            logger.debug("Attempted to format None as trend")
            return ''
        
        # Get the string representation and convert to title case
        trend_name = str(trend).capitalize()
        
        # Add symbol if requested
        if include_symbol:
            symbol = TREND_SYMBOLS.get(trend, '')
            return f"{trend_name} {symbol}".strip()
        else:
            return trend_name
    
    except Exception as e:
        logger.error(f"Error formatting trend: {e}")
        # Return the trend name as fallback
        return str(trend).capitalize() if trend is not None else ''


def format_date(date: datetime.date, 
               format_string: typing.Optional[str] = None) -> str:
    """
    Formats a date object as a string using standard format.
    
    Args:
        date: Date to format
        format_string: Optional custom format string (default: DATE_FORMAT)
        
    Returns:
        Formatted date string
    """
    try:
        if date is None:
            logger.debug("Attempted to format None as date")
            return ''
        
        # Use default format if not specified
        if format_string is None:
            format_string = DATE_FORMAT
        
        # Format the date
        return date.strftime(format_string)
    
    except Exception as e:
        logger.error(f"Error formatting date: {e}")
        # Return ISO format as fallback
        try:
            return date.isoformat() if date is not None else ''
        except:
            return str(date) if date is not None else ''


def format_date_range(start_date: datetime.date, end_date: datetime.date,
                    format_string: typing.Optional[str] = None,
                    separator: typing.Optional[str] = None) -> str:
    """
    Formats a date range as a string.
    
    Args:
        start_date: Start date
        end_date: End date
        format_string: Optional custom format string (default: DATE_FORMAT)
        separator: Optional custom separator (default: ' to ')
        
    Returns:
        Formatted date range string
    """
    try:
        if start_date is None or end_date is None:
            logger.debug("Attempted to format None as date range")
            return ''
        
        # Use default separator if not specified
        if separator is None:
            separator = ' to '
        
        # Format each date
        start_formatted = format_date(start_date, format_string)
        end_formatted = format_date(end_date, format_string)
        
        # Combine with separator
        return f"{start_formatted}{separator}{end_formatted}"
    
    except Exception as e:
        logger.error(f"Error formatting date range: {e}")
        # Return a basic format as fallback
        return f"{start_date} to {end_date}" if start_date is not None and end_date is not None else ''


def format_time_period(start_date: datetime.date, end_date: datetime.date,
                      granularity: GranularityType) -> str:
    """
    Formats a time period with granularity information.
    
    Args:
        start_date: Start date
        end_date: End date
        granularity: Time period granularity
        
    Returns:
        Formatted time period string
    """
    try:
        if start_date is None or end_date is None or granularity is None:
            logger.debug("Attempted to format incomplete time period")
            return ''
        
        # Format the date range
        date_range = format_date_range(start_date, end_date)
        
        # Get the granularity label
        granularity_label = GRANULARITY_LABELS.get(granularity, str(granularity).capitalize())
        
        # Combine
        return f"{date_range} ({granularity_label})"
    
    except Exception as e:
        logger.error(f"Error formatting time period: {e}")
        # Return a basic format as fallback
        granularity_str = str(granularity).capitalize() if granularity is not None else 'Unknown'
        return f"{start_date} to {end_date} ({granularity_str})" if start_date is not None and end_date is not None else ''


def format_json_value(value: typing.Any) -> typing.Any:
    """
    Formats a value for JSON serialization, handling non-serializable types.
    
    Args:
        value: The value to format for JSON serialization
        
    Returns:
        JSON-serializable value
    """
    try:
        # Handle None
        if value is None:
            return None
        
        # Handle Decimal
        if isinstance(value, Decimal):
            return float(value)
        
        # Handle datetime
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        
        # Handle date
        if isinstance(value, datetime.date):
            return value.isoformat()
        
        # Handle enums
        if isinstance(value, TrendDirection) or hasattr(value, '__members__'):
            return str(value)
        
        # Handle dictionaries (recursively)
        if isinstance(value, dict):
            return {k: format_json_value(v) for k, v in value.items()}
        
        # Handle lists and tuples (recursively)
        if isinstance(value, (list, tuple)):
            return [format_json_value(item) for item in value]
        
        # Return the value as is if it's already serializable
        return value
    
    except Exception as e:
        logger.error(f"Error formatting value for JSON: {e}")
        # Return string representation as fallback
        return str(value)


def format_number(value: typing.Union[decimal.Decimal, float, int],
                 precision: typing.Optional[int] = None) -> str:
    """
    Formats a numeric value with thousands separators and decimal places.
    
    Args:
        value: Numeric value to format
        precision: Number of decimal places (default: DISPLAY_PRECISION)
        
    Returns:
        Formatted number string
    """
    try:
        if value is None:
            logger.debug("Attempted to format None as number")
            return ''
        
        # Use default precision if not specified
        if precision is None:
            precision = DISPLAY_PRECISION
        
        # Convert to Decimal for consistent formatting
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Round to specified precision
        rounded_value = value.quantize(
            Decimal('0.' + '0' * precision),
            rounding=decimal.ROUND_HALF_UP
        )
        
        # Format with thousand separators and fixed decimal places
        return f"{rounded_value:,.{precision}f}"
    
    except Exception as e:
        logger.error(f"Error formatting number: {e}")
        # Return basic string as fallback
        return str(value) if value is not None else ''


def truncate_text(text: str, max_length: int, 
                 suffix: typing.Optional[str] = None) -> str:
    """
    Truncates text to a specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: String to append when truncated (default: '...')
        
    Returns:
        Truncated text
    """
    try:
        if text is None:
            logger.debug("Attempted to truncate None")
            return ''
        
        # Use default suffix if not specified
        if suffix is None:
            suffix = '...'
        
        # Return unchanged if it's short enough
        if len(text) <= max_length:
            return text
        
        # Truncate and add suffix
        truncated = text[:max_length - len(suffix)]
        return truncated + suffix
    
    except Exception as e:
        logger.error(f"Error truncating text: {e}")
        # Return original text as fallback
        return text if text is not None else ''