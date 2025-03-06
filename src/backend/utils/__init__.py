#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialization module for the utils package that exports utility functions and classes for the Freight Price Movement Agent.
This module makes key utility functions available through a clean, organized interface to simplify imports throughout the application.
"""

# Import calculation utilities for price movement analysis
from .calculation import (
    calculate_absolute_change,
    calculate_percentage_change,
    determine_trend_direction,
    calculate_statistics,
    calculate_moving_average,
    normalize_values,
    aggregate_by_period,
    calculate_price_movement
)

# Import CSV parsing utilities for data ingestion
from .csv_parser import (
    read_csv_file,
    validate_csv_structure,
    map_columns,
    standardize_date_format,
    validate_freight_data,
    clean_freight_data,
    CSVValidator,
    CSVProcessor
)

# Import currency utilities for handling different currencies
from .currency import (
    convert_currency,
    get_exchange_rate,
    normalize_to_default_currency,
    format_currency,
    get_currency_symbol,
    is_valid_currency_code,
    CurrencyConverter
)

# Import date utilities for time period handling
from .date_utils import (
    parse_date,
    format_date,
    format_datetime,
    to_iso_format,
    now,
    today,
    convert_timezone,
    normalize_to_utc,
    add_days,
    add_weeks,
    add_months,
    add_quarters,
    date_diff_days,
    date_diff_weeks,
    date_diff_months,
    date_diff_quarters,
    get_start_of_day,
    get_end_of_day,
    get_start_of_week,
    get_end_of_week,
    get_start_of_month,
    get_end_of_month,
    get_start_of_quarter,
    get_end_of_quarter,
    generate_date_periods,
    is_same_day,
    is_future_date,
    is_past_date,
    get_date_range_description
)

# Import visualization utilities for generating charts
from .visualization import (
    generate_line_chart,
    generate_bar_chart,
    generate_trend_indicator,
    generate_comparison_chart,
    encode_image_base64
)

__all__ = [
    'calculate_absolute_change',  # Calculate absolute difference between end and start values
    'calculate_percentage_change',  # Calculate percentage change between end and start values
    'determine_trend_direction',  # Determine if trend is increasing, decreasing, or stable
    'calculate_statistics',  # Calculate statistical measures for a series of values
    'calculate_moving_average',  # Calculate moving average for time series data
    'normalize_values',  # Normalize values to a common currency
    'aggregate_by_period',  # Aggregate freight data by time periods
    'calculate_price_movement',  # Calculate comprehensive price movement metrics
    'read_csv_file',  # Read CSV files into pandas DataFrames
    'validate_csv_structure',  # Validate CSV structure against required columns
    'map_columns',  # Map source columns to standardized schema
    'standardize_date_format',  # Convert dates to standardized format
    'validate_freight_data',  # Validate freight data against business rules
    'clean_freight_data',  # Clean and standardize freight data
    'CSVValidator',  # CSV validation capabilities
    'CSVProcessor',  # End-to-end CSV processing for freight data
    'convert_currency',  # Convert amount from one currency to another
    'get_exchange_rate',  # Get exchange rate between two currencies
    'normalize_to_default_currency',  # Convert amount to system default currency
    'format_currency',  # Format currency amount with proper formatting
    'is_valid_currency_code',  # Validate if a string is a valid currency code
    'CurrencyConverter',  # Class for handling currency conversions with caching
    'parse_date',  # Parse date strings into datetime objects
    'format_date',  # Format datetime objects as date strings
    'format_datetime',  # Format datetime objects as datetime strings
    'to_iso_format',  # Convert datetime objects to ISO 8601 format
    'now',  # Get current datetime with timezone
    'today',  # Get current date at midnight
    'generate_date_periods', # Generate list of date periods based on granularity
    'is_future_date', # Check if a date is in the future
    'is_past_date', # Check if a date is in the past
    'generate_line_chart',  # Generate line charts for time series freight price data
    'generate_bar_chart',  # Generate bar charts for comparing freight prices across categories
    'generate_trend_indicator',  # Generate visual indicators for price movement trend direction
    'generate_comparison_chart', # Generate charts comparing two time periods of freight price data
    'convert_timezone', # Convert a datetime from one timezone to another
    'normalize_to_utc', # Normalize a datetime to UTC timezone
    'add_days', # Add a specified number of days to a datetime
    'add_weeks', # Add a specified number of weeks to a datetime
    'add_months', # Add a specified number of months to a datetime
    'add_quarters', # Add a specified number of quarters to a datetime
    'date_diff_days', # Calculate the difference between two dates in days
    'date_diff_weeks', # Calculate the difference between two dates in weeks
    'date_diff_months', # Calculate the approximate difference between two dates in months
    'date_diff_quarters', # Calculate the approximate difference between two dates in quarters
    'get_start_of_day', # Get the start of the day (midnight) for a given datetime
    'get_end_of_day', # Get the end of the day (23:59:59) for a given datetime
    'get_start_of_week', # Get the start of the week (Monday) for a given datetime
    'get_end_of_week', # Get the end of the week (Sunday) for a given datetime
    'get_start_of_month', # Get the start of the month for a given datetime
    'get_end_of_month', # Get the end of the month for a given datetime
    'get_start_of_quarter', # Get the start of the quarter for a given datetime
    'get_end_of_quarter', # Get the end of the quarter for a given datetime
    'get_date_range_description' # Generate a human-readable description of a date range
]