#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core calculation utility module for the Freight Price Movement Agent.

This module provides functions for calculating absolute changes, percentage changes,
and determining trend directions based on freight pricing data.
"""

import decimal
from decimal import Decimal
import typing

import numpy as np
import pandas as pd

from ..models.enums import TrendDirection, INCREASING, DECREASING, STABLE, from_percentage
from .currency import convert_currency
from ..core.logging import logger

# Constants for trend classification
TREND_THRESHOLD_INCREASE = Decimal('1.0')  # Percentage threshold for increasing trend
TREND_THRESHOLD_DECREASE = Decimal('-1.0')  # Percentage threshold for decreasing trend
CALCULATION_PRECISION = 4  # Decimal places for calculation results


def calculate_absolute_change(start_value: decimal.Decimal, end_value: decimal.Decimal) -> decimal.Decimal:
    """
    Calculates the absolute change between start and end values.
    
    Args:
        start_value: Initial freight charge
        end_value: Final freight charge
        
    Returns:
        Absolute change (end_value - start_value)
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        # Validate inputs
        if start_value is None or end_value is None:
            raise ValueError("Start and end values cannot be None")
        
        # Calculate absolute change
        absolute_change = end_value - start_value
        
        # Round to specified precision
        absolute_change = absolute_change.quantize(
            Decimal('0.' + '0' * CALCULATION_PRECISION),
            rounding=decimal.ROUND_HALF_UP
        )
        
        logger.debug(f"Calculated absolute change: {absolute_change} (from {start_value} to {end_value})")
        return absolute_change
    
    except Exception as e:
        logger.error(f"Error calculating absolute change: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to calculate absolute change: {str(e)}") from e


def calculate_percentage_change(start_value: decimal.Decimal, end_value: decimal.Decimal) -> decimal.Decimal:
    """
    Calculates the percentage change between start and end values.
    
    Args:
        start_value: Initial freight charge
        end_value: Final freight charge
        
    Returns:
        Percentage change ((end_value - start_value) / start_value * 100)
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        # Validate inputs
        if start_value is None or end_value is None:
            raise ValueError("Start and end values cannot be None")
        
        # Handle special cases
        if start_value == Decimal('0'):
            if end_value > Decimal('0'):
                # New rate established
                logger.info(f"Special case: start_value is 0, end_value is {end_value} > 0")
                # Return a large positive value to indicate new rate established
                return Decimal('9999.9999')
            
            if end_value == Decimal('0'):
                # No change
                logger.info("Special case: start_value and end_value are both 0")
                return Decimal('0')
        
        if start_value > Decimal('0') and end_value == Decimal('0'):
            # Complete decrease
            logger.info(f"Special case: start_value is {start_value} > 0, end_value is 0")
            return Decimal('-100')
        
        # Normal case
        absolute_change = calculate_absolute_change(start_value, end_value)
        percentage_change = (absolute_change / start_value) * Decimal('100')
        
        # Round to specified precision
        percentage_change = percentage_change.quantize(
            Decimal('0.' + '0' * CALCULATION_PRECISION),
            rounding=decimal.ROUND_HALF_UP
        )
        
        logger.debug(f"Calculated percentage change: {percentage_change}% (from {start_value} to {end_value})")
        return percentage_change
    
    except Exception as e:
        logger.error(f"Error calculating percentage change: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to calculate percentage change: {str(e)}") from e


def determine_trend_direction(percentage_change: decimal.Decimal) -> TrendDirection:
    """
    Determines the trend direction based on percentage change.
    
    Args:
        percentage_change: Percentage change value
        
    Returns:
        TrendDirection enum value (INCREASING, DECREASING, or STABLE)
        
    Raises:
        ValueError: If input is invalid
    """
    try:
        # Validate input
        if percentage_change is None:
            raise ValueError("Percentage change cannot be None")
        
        # Use TrendDirection.from_percentage method to determine trend direction
        trend_direction = TrendDirection.from_percentage(percentage_change)
        logger.debug(f"Determined trend direction: {trend_direction.name} for percentage change of {percentage_change}%")
        return trend_direction
    
    except Exception as e:
        logger.error(f"Error determining trend direction: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to determine trend direction: {str(e)}") from e


def calculate_statistics(values: typing.List[decimal.Decimal]) -> typing.Dict[str, decimal.Decimal]:
    """
    Calculates statistical measures for a series of freight charges.
    
    Args:
        values: List of freight charges
        
    Returns:
        Dictionary of statistical measures (mean, min, max, std_dev, median, variance)
        
    Raises:
        ValueError: If input is invalid
    """
    try:
        # Validate input
        if not values:
            raise ValueError("Values list cannot be empty")
        
        # Convert to numpy array for statistical calculations
        values_array = np.array([float(v) for v in values])
        
        # Calculate statistics
        mean = Decimal(str(np.mean(values_array)))
        minimum = Decimal(str(np.min(values_array)))
        maximum = Decimal(str(np.max(values_array)))
        std_dev = Decimal(str(np.std(values_array)))
        median = Decimal(str(np.median(values_array)))
        variance = Decimal(str(np.var(values_array)))
        
        # Round to specified precision
        precision = Decimal('0.' + '0' * CALCULATION_PRECISION)
        mean = mean.quantize(precision, rounding=decimal.ROUND_HALF_UP)
        minimum = minimum.quantize(precision, rounding=decimal.ROUND_HALF_UP)
        maximum = maximum.quantize(precision, rounding=decimal.ROUND_HALF_UP)
        std_dev = std_dev.quantize(precision, rounding=decimal.ROUND_HALF_UP)
        median = median.quantize(precision, rounding=decimal.ROUND_HALF_UP)
        variance = variance.quantize(precision, rounding=decimal.ROUND_HALF_UP)
        
        # Compile results
        stats = {
            'mean': mean,
            'min': minimum,
            'max': maximum,
            'std_dev': std_dev,
            'median': median,
            'variance': variance
        }
        
        logger.debug(f"Calculated statistics for {len(values)} values: mean={mean}, min={minimum}, max={maximum}")
        return stats
    
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to calculate statistics: {str(e)}") from e


def calculate_moving_average(values: typing.List[decimal.Decimal], window_size: int) -> typing.List[typing.Optional[decimal.Decimal]]:
    """
    Calculates moving average for a time series of freight charges.
    
    Args:
        values: List of freight charges
        window_size: Size of the moving window
        
    Returns:
        List of moving averages with None values for positions where average cannot be calculated
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        # Validate inputs
        if values is None:
            raise ValueError("Values list cannot be None")
        
        if not window_size or window_size <= 0:
            raise ValueError("Window size must be a positive integer")
        
        # If the list is shorter than window_size, return None for all positions
        if len(values) < window_size:
            logger.warning(f"Values list length ({len(values)}) is less than window size ({window_size})")
            return [None] * len(values)
        
        # Initialize result list with None values for the first window_size-1 positions
        result = [None] * (window_size - 1)
        
        # Calculate moving averages for each valid position
        for i in range(window_size - 1, len(values)):
            window = values[i - window_size + 1:i + 1]
            window_sum = sum(window)
            average = window_sum / Decimal(str(window_size))
            
            # Round to specified precision
            average = average.quantize(
                Decimal('0.' + '0' * CALCULATION_PRECISION),
                rounding=decimal.ROUND_HALF_UP
            )
            
            result.append(average)
        
        logger.debug(f"Calculated moving averages with window size {window_size} for {len(values)} values")
        return result
    
    except Exception as e:
        logger.error(f"Error calculating moving average: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to calculate moving average: {str(e)}") from e


def normalize_values(values_with_currency: typing.List[typing.Tuple[decimal.Decimal, str]], 
                    target_currency: typing.Optional[str] = None) -> typing.List[decimal.Decimal]:
    """
    Normalizes a list of values to a common currency.
    
    Args:
        values_with_currency: List of (value, currency) tuples
        target_currency: Currency to normalize to (defaults to first value's currency)
        
    Returns:
        List of normalized values in target currency
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        # Validate input
        if not values_with_currency:
            raise ValueError("Values list cannot be empty")
        
        # If target_currency is None, use the currency of the first value
        if target_currency is None:
            target_currency = values_with_currency[0][1]
            logger.info(f"Target currency not specified, using {target_currency} from first value")
        
        normalized_values = []
        
        # For each (value, currency) pair in values_with_currency:
        for value, currency in values_with_currency:
            if currency == target_currency:
                # If currency matches target_currency, add value directly to result
                normalized_values.append(value)
            else:
                # Otherwise, convert value to target_currency using convert_currency()
                converted_value = convert_currency(value, currency, target_currency)
                normalized_values.append(converted_value)
        
        logger.debug(f"Normalized {len(values_with_currency)} values to {target_currency}")
        return normalized_values
    
    except Exception as e:
        logger.error(f"Error normalizing values: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to normalize values: {str(e)}") from e


def aggregate_by_period(freight_data: pd.DataFrame, 
                       date_column: str, 
                       value_column: str, 
                       period_type: str) -> pd.DataFrame:
    """
    Aggregates freight charges by time period.
    
    Args:
        freight_data: DataFrame containing freight data
        date_column: Name of the date column
        value_column: Name of the value column to aggregate
        period_type: Type of period ('D' for daily, 'W' for weekly, 'M' for monthly, 'Q' for quarterly)
        
    Returns:
        Aggregated DataFrame by period
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        # Validate inputs
        if freight_data is None or freight_data.empty:
            raise ValueError("Freight data cannot be None or empty")
        
        if date_column not in freight_data.columns:
            raise ValueError(f"Date column '{date_column}' not found in data")
        
        if value_column not in freight_data.columns:
            raise ValueError(f"Value column '{value_column}' not found in data")
        
        # Ensure date_column is datetime type
        freight_data = freight_data.copy()
        if not pd.api.types.is_datetime64_any_dtype(freight_data[date_column]):
            freight_data[date_column] = pd.to_datetime(freight_data[date_column])
        
        # Validate period_type
        valid_periods = {'D', 'W', 'M', 'Q'}
        if period_type not in valid_periods:
            raise ValueError(f"Invalid period type '{period_type}'. Must be one of {valid_periods}")
        
        # Set the date_column as index
        freight_data.set_index(date_column, inplace=True)
        
        # Resample the data based on period_type and aggregate value_column
        aggregated = freight_data[value_column].resample(period_type).mean()
        
        # Reset index to make date_column a regular column again
        aggregated = aggregated.reset_index()
        
        logger.debug(f"Aggregated {len(freight_data)} records to {len(aggregated)} periods by {period_type}")
        return aggregated
    
    except Exception as e:
        logger.error(f"Error aggregating by period: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to aggregate by period: {str(e)}") from e


def calculate_price_movement(time_series: typing.List[typing.Dict[str, typing.Any]], 
                            value_key: str) -> typing.Dict[str, typing.Any]:
    """
    Calculates price movement metrics for a time series of freight data.
    
    Args:
        time_series: List of time series data points
        value_key: Key for value in each data point
        
    Returns:
        Dictionary containing price movement analysis results
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        # Validate inputs
        if not time_series:
            raise ValueError("Time series data cannot be empty")
        
        if value_key not in time_series[0]:
            raise ValueError(f"Value key '{value_key}' not found in time series data")
        
        # Extract start_value from the first entry in time_series
        start_value = Decimal(str(time_series[0][value_key]))
        
        # Extract end_value from the last entry in time_series
        end_value = Decimal(str(time_series[-1][value_key]))
        
        # Calculate absolute_change using calculate_absolute_change()
        absolute_change = calculate_absolute_change(start_value, end_value)
        
        # Calculate percentage_change using calculate_percentage_change()
        percentage_change = calculate_percentage_change(start_value, end_value)
        
        # Determine trend_direction using determine_trend_direction()
        trend_direction = determine_trend_direction(percentage_change)
        
        # Extract all values from time_series for statistical analysis
        values = [Decimal(str(point[value_key])) for point in time_series]
        
        # Calculate statistics using calculate_statistics()
        statistics = calculate_statistics(values)
        
        # Compile all results into a structured dictionary
        results = {
            'start_value': start_value,
            'end_value': end_value,
            'absolute_change': absolute_change,
            'percentage_change': percentage_change,
            'trend_direction': trend_direction.name,
            'statistics': statistics,
            'data_points': len(time_series)
        }
        
        logger.info(f"Calculated price movement: {percentage_change}% change ({absolute_change} absolute), trend: {trend_direction.name}")
        return results
    
    except Exception as e:
        logger.error(f"Error calculating price movement: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to calculate price movement: {str(e)}") from e