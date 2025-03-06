"""
Date and time utility functions for the Freight Price Movement Agent.

This module provides comprehensive date and time manipulation capabilities including
parsing, formatting, arithmetic operations, period calculations, and timezone handling.
These utilities support the time period selection and analysis features of the application.
"""

import datetime
from dateutil import parser
from dateutil import relativedelta
import pytz
from typing import List, Optional, Tuple, Union

# Default timezone and date format constants
DEFAULT_TIMEZONE = pytz.UTC
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def parse_date(date_string: str, format_string: Optional[str] = None, 
               timezone: Optional[datetime.tzinfo] = None) -> datetime.datetime:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_string: String representation of a date/datetime
        format_string: Optional format string for parsing (if None, uses flexible parsing)
        timezone: Optional timezone to assign to the parsed datetime
        
    Returns:
        A datetime object representing the parsed date
        
    Raises:
        ValueError: If the date string cannot be parsed
    """
    try:
        if format_string:
            # Parse using the specified format
            parsed_date = datetime.datetime.strptime(date_string, format_string)
        else:
            # Use flexible parsing
            parsed_date = parser.parse(date_string)
        
        # Handle timezone
        if timezone:
            if parsed_date.tzinfo is None:
                # Assign timezone to naive datetime
                parsed_date = parsed_date.replace(tzinfo=timezone)
            else:
                # Convert to specified timezone
                parsed_date = parsed_date.astimezone(timezone)
        elif parsed_date.tzinfo is None:
            # If no timezone specified and parsed date is naive, use default
            parsed_date = parsed_date.replace(tzinfo=DEFAULT_TIMEZONE)
            
        return parsed_date
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to parse date string '{date_string}': {str(e)}")


def format_date(dt: datetime.datetime, format_string: Optional[str] = None) -> str:
    """
    Format a datetime object as a date string.
    
    Args:
        dt: The datetime object to format
        format_string: Optional format string (defaults to DATE_FORMAT)
        
    Returns:
        Formatted date string
        
    Raises:
        ValueError: If the datetime cannot be formatted
    """
    try:
        if format_string is None:
            format_string = DATE_FORMAT
        return dt.strftime(format_string)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to format datetime {dt}: {str(e)}")


def format_datetime(dt: datetime.datetime, format_string: Optional[str] = None) -> str:
    """
    Format a datetime object as a string with time component.
    
    Args:
        dt: The datetime object to format
        format_string: Optional format string (defaults to DATETIME_FORMAT)
        
    Returns:
        Formatted datetime string
        
    Raises:
        ValueError: If the datetime cannot be formatted
    """
    try:
        if format_string is None:
            format_string = DATETIME_FORMAT
        return dt.strftime(format_string)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to format datetime {dt}: {str(e)}")


def to_iso_format(dt: datetime.datetime) -> str:
    """
    Convert a datetime object to ISO 8601 format string.
    
    Args:
        dt: The datetime object to format
        
    Returns:
        ISO formatted datetime string
        
    Raises:
        ValueError: If the datetime cannot be formatted
    """
    try:
        # Ensure datetime has timezone information
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=DEFAULT_TIMEZONE)
        return dt.isoformat()
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to convert datetime to ISO format: {str(e)}")


def now(timezone: Optional[datetime.tzinfo] = None) -> datetime.datetime:
    """
    Get the current datetime with timezone information.
    
    Args:
        timezone: Optional timezone (defaults to DEFAULT_TIMEZONE)
        
    Returns:
        Current datetime with timezone
    """
    current = datetime.datetime.now()
    if timezone is None:
        timezone = DEFAULT_TIMEZONE
    
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone)
    else:
        current = current.astimezone(timezone)
    
    return current


def today(timezone: Optional[datetime.tzinfo] = None) -> datetime.datetime:
    """
    Get the current date (without time component).
    
    Args:
        timezone: Optional timezone (defaults to DEFAULT_TIMEZONE)
        
    Returns:
        Current date at midnight
    """
    current = now(timezone)
    return current.replace(hour=0, minute=0, second=0, microsecond=0)


def convert_timezone(dt: datetime.datetime, target_timezone: datetime.tzinfo) -> datetime.datetime:
    """
    Convert a datetime from one timezone to another.
    
    Args:
        dt: The datetime to convert
        target_timezone: The target timezone
        
    Returns:
        Datetime in target timezone
        
    Raises:
        ValueError: If the datetime cannot be converted
    """
    try:
        # Ensure datetime has timezone information
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=DEFAULT_TIMEZONE)
        
        # Convert to target timezone
        return dt.astimezone(target_timezone)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to convert timezone: {str(e)}")


def normalize_to_utc(dt: datetime.datetime) -> datetime.datetime:
    """
    Normalize a datetime to UTC timezone.
    
    Args:
        dt: The datetime to normalize
        
    Returns:
        Datetime in UTC timezone
    """
    return convert_timezone(dt, pytz.UTC)


def add_days(dt: datetime.datetime, days: int) -> datetime.datetime:
    """
    Add a specified number of days to a datetime.
    
    Args:
        dt: The base datetime
        days: Number of days to add (can be negative)
        
    Returns:
        Datetime with days added
        
    Raises:
        ValueError: If the operation fails
    """
    try:
        return dt + datetime.timedelta(days=days)
    except (ValueError, TypeError, OverflowError) as e:
        raise ValueError(f"Failed to add {days} days to datetime: {str(e)}")


def add_weeks(dt: datetime.datetime, weeks: int) -> datetime.datetime:
    """
    Add a specified number of weeks to a datetime.
    
    Args:
        dt: The base datetime
        weeks: Number of weeks to add (can be negative)
        
    Returns:
        Datetime with weeks added
        
    Raises:
        ValueError: If the operation fails
    """
    try:
        return dt + datetime.timedelta(weeks=weeks)
    except (ValueError, TypeError, OverflowError) as e:
        raise ValueError(f"Failed to add {weeks} weeks to datetime: {str(e)}")


def add_months(dt: datetime.datetime, months: int) -> datetime.datetime:
    """
    Add a specified number of months to a datetime.
    
    Args:
        dt: The base datetime
        months: Number of months to add (can be negative)
        
    Returns:
        Datetime with months added
        
    Raises:
        ValueError: If the operation fails
    """
    try:
        return dt + relativedelta.relativedelta(months=months)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to add {months} months to datetime: {str(e)}")


def add_quarters(dt: datetime.datetime, quarters: int) -> datetime.datetime:
    """
    Add a specified number of quarters (3-month periods) to a datetime.
    
    Args:
        dt: The base datetime
        quarters: Number of quarters to add (can be negative)
        
    Returns:
        Datetime with quarters added
    """
    return add_months(dt, quarters * 3)


def date_diff_days(start_date: datetime.datetime, end_date: datetime.datetime) -> int:
    """
    Calculate the difference between two dates in days.
    
    Args:
        start_date: The earlier datetime
        end_date: The later datetime
        
    Returns:
        Number of days between dates
        
    Raises:
        ValueError: If the calculation fails
    """
    try:
        delta = end_date - start_date
        return abs(delta.days)
    except (ValueError, TypeError, OverflowError) as e:
        raise ValueError(f"Failed to calculate days between dates: {str(e)}")


def date_diff_weeks(start_date: datetime.datetime, end_date: datetime.datetime) -> float:
    """
    Calculate the difference between two dates in weeks.
    
    Args:
        start_date: The earlier datetime
        end_date: The later datetime
        
    Returns:
        Number of weeks between dates (rounded to 2 decimal places)
    """
    days = date_diff_days(start_date, end_date)
    weeks = days / 7
    return round(weeks, 2)


def date_diff_months(start_date: datetime.datetime, end_date: datetime.datetime) -> int:
    """
    Calculate the approximate difference between two dates in months.
    
    Args:
        start_date: The earlier datetime
        end_date: The later datetime
        
    Returns:
        Number of months between dates
        
    Raises:
        ValueError: If the calculation fails
    """
    try:
        # Normalize dates to same timezone if they have timezone info
        if start_date.tzinfo and end_date.tzinfo:
            start_date = normalize_to_utc(start_date)
            end_date = normalize_to_utc(end_date)
        
        # Ensure start_date is before end_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        # Calculate using relativedelta
        delta = relativedelta.relativedelta(end_date, start_date)
        months = delta.months + delta.years * 12
        
        return months
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to calculate months between dates: {str(e)}")


def date_diff_quarters(start_date: datetime.datetime, end_date: datetime.datetime) -> float:
    """
    Calculate the approximate difference between two dates in quarters.
    
    Args:
        start_date: The earlier datetime
        end_date: The later datetime
        
    Returns:
        Number of quarters between dates (rounded to 2 decimal places)
    """
    months = date_diff_months(start_date, end_date)
    quarters = months / 3
    return round(quarters, 2)


def get_start_of_day(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the start of the day (midnight) for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at start of day
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the end of the day (23:59:59) for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at end of day
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_start_of_week(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the start of the week (Monday) for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at start of week
    """
    # Subtract days to get to Monday (weekday() returns 0 for Monday)
    days_to_subtract = dt.weekday()
    start_of_week = dt - datetime.timedelta(days=days_to_subtract)
    return get_start_of_day(start_of_week)


def get_end_of_week(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the end of the week (Sunday) for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at end of week
    """
    # Add days to get to Sunday (6 - weekday() gives days to add)
    days_to_add = 6 - dt.weekday()
    end_of_week = dt + datetime.timedelta(days=days_to_add)
    return get_end_of_day(end_of_week)


def get_start_of_month(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the start of the month for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at start of month
    """
    start_of_month = dt.replace(day=1)
    return get_start_of_day(start_of_month)


def get_end_of_month(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the end of the month for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at end of month
    """
    # Get the first day of next month, then subtract one day
    next_month = dt.replace(day=1) + relativedelta.relativedelta(months=1)
    end_of_month = next_month - datetime.timedelta(days=1)
    return get_end_of_day(end_of_month)


def get_start_of_quarter(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the start of the quarter for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at start of quarter
    """
    # Calculate the first month of the quarter (1, 4, 7, or 10)
    quarter_month = (dt.month - 1) // 3 * 3 + 1
    start_of_quarter = dt.replace(month=quarter_month, day=1)
    return get_start_of_day(start_of_quarter)


def get_end_of_quarter(dt: datetime.datetime) -> datetime.datetime:
    """
    Get the end of the quarter for a given datetime.
    
    Args:
        dt: The input datetime
        
    Returns:
        Datetime at end of quarter
    """
    # Get the start of the quarter, add 3 months, subtract one day
    start_of_next_quarter = add_months(get_start_of_quarter(dt), 3)
    end_of_quarter = start_of_next_quarter - datetime.timedelta(days=1)
    return get_end_of_day(end_of_quarter)


def generate_date_periods(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    granularity: str,
    custom_interval_days: Optional[int] = None
) -> List[Tuple[datetime.datetime, datetime.datetime]]:
    """
    Generate a list of date periods based on the specified granularity.
    
    Args:
        start_date: The start datetime of the overall period
        end_date: The end datetime of the overall period
        granularity: The granularity of periods ('daily', 'weekly', 'monthly', 
                     'quarterly', or 'custom')
        custom_interval_days: Number of days in each period when granularity is 'custom'
        
    Returns:
        List of tuples containing (period_start, period_end) datetimes
        
    Raises:
        ValueError: If dates are invalid or granularity is not supported
    """
    if start_date > end_date:
        raise ValueError("Start date must be before end date")
    
    periods = []
    current_start = start_date
    
    if granularity == 'daily':
        while current_start < end_date:
            current_end = get_end_of_day(current_start)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start, current_end))
            current_start = add_days(get_start_of_day(current_start), 1)
    
    elif granularity == 'weekly':
        # Adjust to start of week
        current_start = get_start_of_week(current_start)
        while current_start < end_date:
            current_end = get_end_of_week(current_start)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start, current_end))
            current_start = add_days(current_start, 7)
    
    elif granularity == 'monthly':
        # Adjust to start of month
        current_start = get_start_of_month(current_start)
        while current_start < end_date:
            current_end = get_end_of_month(current_start)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start, current_end))
            current_start = add_months(current_start, 1)
    
    elif granularity == 'quarterly':
        # Adjust to start of quarter
        current_start = get_start_of_quarter(current_start)
        while current_start < end_date:
            current_end = get_end_of_quarter(current_start)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start, current_end))
            current_start = add_months(current_start, 3)
    
    elif granularity == 'custom':
        if custom_interval_days is None or custom_interval_days <= 0:
            raise ValueError("Custom interval days must be a positive integer")
        
        while current_start < end_date:
            current_end = add_days(current_start, custom_interval_days - 1)
            current_end = get_end_of_day(current_end)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start, current_end))
            current_start = add_days(get_start_of_day(current_start), custom_interval_days)
    
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")
    
    return periods


def is_same_day(dt1: datetime.datetime, dt2: datetime.datetime) -> bool:
    """
    Check if two datetimes fall on the same day.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        True if same day, False otherwise
    """
    # Normalize to same timezone if they have timezone info
    if dt1.tzinfo and dt2.tzinfo:
        dt1 = normalize_to_utc(dt1)
        dt2 = normalize_to_utc(dt2)
    
    return (dt1.year == dt2.year and 
            dt1.month == dt2.month and 
            dt1.day == dt2.day)


def is_future_date(dt: datetime.datetime, reference_date: Optional[datetime.datetime] = None) -> bool:
    """
    Check if a date is in the future.
    
    Args:
        dt: The datetime to check
        reference_date: The reference datetime (defaults to current datetime)
        
    Returns:
        True if future date, False otherwise
    """
    if reference_date is None:
        reference_date = now()
    
    # Normalize to same timezone if they have timezone info
    if dt.tzinfo and reference_date.tzinfo:
        dt = normalize_to_utc(dt)
        reference_date = normalize_to_utc(reference_date)
    
    return dt > reference_date


def is_past_date(dt: datetime.datetime, reference_date: Optional[datetime.datetime] = None) -> bool:
    """
    Check if a date is in the past.
    
    Args:
        dt: The datetime to check
        reference_date: The reference datetime (defaults to current datetime)
        
    Returns:
        True if past date, False otherwise
    """
    if reference_date is None:
        reference_date = now()
    
    # Normalize to same timezone if they have timezone info
    if dt.tzinfo and reference_date.tzinfo:
        dt = normalize_to_utc(dt)
        reference_date = normalize_to_utc(reference_date)
    
    return dt < reference_date


def get_date_range_description(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    format_string: Optional[str] = None
) -> str:
    """
    Generate a human-readable description of a date range.
    
    Args:
        start_date: The start datetime
        end_date: The end datetime
        format_string: Optional format string for dates
        
    Returns:
        Human-readable date range description
        
    Raises:
        ValueError: If the formatting fails
    """
    try:
        start_str = format_date(start_date, format_string)
        end_str = format_date(end_date, format_string)
        return f"{start_str} to {end_str}"
    except ValueError as e:
        raise ValueError(f"Failed to create date range description: {str(e)}")