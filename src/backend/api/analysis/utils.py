#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for the analysis API module of the Freight Price Movement Agent.

This module provides helper functions for building queries, calculating price
movements, formatting results, and managing caching for analysis operations.
"""

import datetime
import decimal
from decimal import Decimal
import hashlib
import typing
import json
import csv
import io
import uuid
from typing import Dict, List, Optional, Union, Any, Tuple

import sqlalchemy
from sqlalchemy import and_, or_, func
from fastapi import HTTPException

from ...core.db import session
from ...models.freight_data import FreightData
from ...models.time_period import TimePeriod
from ...models.enums import GranularityType, TrendDirection, OutputFormat
from .models import AnalysisCache
from ...core.exceptions import AnalysisException
from ...utils.calculation import (
    calculate_absolute_change,
    calculate_percentage_change,
    determine_trend_direction
)
from ...utils.formatters import format_currency, format_percentage
from ...core.logging import logger
from ...core.cache import cache

# Constants
CACHE_PREFIX = 'analysis_'
CACHE_TTL_SECONDS = 3600  # 1 hour


def build_freight_data_query(time_period: TimePeriod, 
                            filters: Optional[List[dict]] = None) -> sqlalchemy.orm.Query:
    """
    Builds a SQLAlchemy query for retrieving freight data based on time period and filters.
    
    Args:
        time_period: TimePeriod model instance defining the date range
        filters: Optional list of filter dictionaries, each containing criteria for filtering
        
    Returns:
        SQLAlchemy query object for freight data
        
    Raises:
        AnalysisException: If query building fails
    """
    try:
        # Start with a base query for FreightData
        query = session.query(FreightData)
        
        # Add filter for record_date between time_period.start_date and time_period.end_date
        query = query.filter(
            FreightData.record_date >= time_period.start_date,
            FreightData.record_date <= time_period.end_date,
            FreightData.is_deleted == False
        )
        
        # Apply additional filters if provided
        if filters:
            for filter_dict in filters:
                # Check for origin_id filter
                if 'origin_id' in filter_dict:
                    origin_ids = filter_dict['origin_id']
                    if isinstance(origin_ids, list):
                        query = query.filter(FreightData.origin_id.in_(origin_ids))
                    else:
                        query = query.filter(FreightData.origin_id == origin_ids)
                
                # Check for destination_id filter
                if 'destination_id' in filter_dict:
                    destination_ids = filter_dict['destination_id']
                    if isinstance(destination_ids, list):
                        query = query.filter(FreightData.destination_id.in_(destination_ids))
                    else:
                        query = query.filter(FreightData.destination_id == destination_ids)
                
                # Check for carrier_id filter
                if 'carrier_id' in filter_dict:
                    carrier_ids = filter_dict['carrier_id']
                    if isinstance(carrier_ids, list):
                        query = query.filter(FreightData.carrier_id.in_(carrier_ids))
                    else:
                        query = query.filter(FreightData.carrier_id == carrier_ids)
                
                # Check for transport_mode filter
                if 'transport_mode' in filter_dict:
                    transport_modes = filter_dict['transport_mode']
                    if isinstance(transport_modes, list):
                        query = query.filter(FreightData.transport_mode.in_(transport_modes))
                    else:
                        query = query.filter(FreightData.transport_mode == transport_modes)
        
        # Order by record_date to ensure consistent results
        query = query.order_by(FreightData.record_date)
        
        logger.debug(f"Built freight data query for time period {time_period.id} with filters: {filters}")
        return query
        
    except Exception as e:
        logger.error(f"Error building freight data query: {str(e)}", exc_info=True)
        raise AnalysisException(f"Failed to build freight data query: {str(e)}")


def group_data_by_granularity(data: List[FreightData], 
                             granularity: GranularityType,
                             custom_interval: Optional[str] = None) -> Dict[datetime.datetime, List[FreightData]]:
    """
    Groups freight data by the specified time granularity.
    
    Args:
        data: List of FreightData records
        granularity: Time granularity type from GranularityType enum
        custom_interval: Optional custom interval specification when granularity is CUSTOM
        
    Returns:
        Dictionary with time period keys and lists of FreightData values
        
    Raises:
        AnalysisException: If grouping fails
    """
    try:
        if not data:
            logger.warning("No data provided for grouping")
            return {}
        
        grouped_data = {}
        
        for record in data:
            record_date = record.record_date
            
            # Determine the time bucket based on granularity
            if granularity == GranularityType.DAILY:
                # Use date part only, reset time to midnight
                bucket = datetime.datetime.combine(record_date.date(), datetime.time.min)
                
            elif granularity == GranularityType.WEEKLY:
                # Start of the week containing record_date (Monday as start of week)
                start_of_week = record_date.date() - datetime.timedelta(days=record_date.weekday())
                bucket = datetime.datetime.combine(start_of_week, datetime.time.min)
                
            elif granularity == GranularityType.MONTHLY:
                # Start of the month containing record_date
                bucket = datetime.datetime(record_date.year, record_date.month, 1)
                
            elif granularity == GranularityType.CUSTOM:
                if not custom_interval or not custom_interval.isdigit():
                    raise AnalysisException("Custom interval must be specified as a number of days")
                
                # Calculate bucket based on days since epoch
                days_since_epoch = (record_date.date() - datetime.date(1970, 1, 1)).days
                interval_days = int(custom_interval)
                bucket_days = (days_since_epoch // interval_days) * interval_days
                bucket_date = datetime.date(1970, 1, 1) + datetime.timedelta(days=bucket_days)
                bucket = datetime.datetime.combine(bucket_date, datetime.time.min)
                
            else:
                raise AnalysisException(f"Unsupported granularity: {granularity}")
            
            # Add the record to the appropriate bucket
            if bucket not in grouped_data:
                grouped_data[bucket] = []
            
            grouped_data[bucket].append(record)
        
        logger.debug(f"Grouped {len(data)} records into {len(grouped_data)} {granularity.name} buckets")
        return grouped_data
        
    except Exception as e:
        if isinstance(e, AnalysisException):
            raise
        logger.error(f"Error grouping data by granularity: {str(e)}", exc_info=True)
        raise AnalysisException(f"Failed to group data by granularity: {str(e)}")


def calculate_price_movement(grouped_data: Dict[datetime.datetime, List[FreightData]],
                           start_date: datetime.date,
                           end_date: datetime.date) -> dict:
    """
    Calculates price movement metrics between start and end periods.
    
    Args:
        grouped_data: Dictionary mapping time periods to lists of FreightData objects
        start_date: Start date for analysis
        end_date: End date for analysis
        
    Returns:
        Dictionary containing price movement metrics (start_value, end_value, 
        absolute_change, percentage_change, trend_direction)
        
    Raises:
        AnalysisException: If calculation fails
    """
    try:
        if not grouped_data:
            raise AnalysisException("No data available for price movement calculation")
        
        # Sort periods by date
        periods = sorted(grouped_data.keys())
        
        # Find the first period (closest to start_date)
        start_period = None
        for period in periods:
            if period.date() >= start_date:
                start_period = period
                break
        
        if start_period is None:
            raise AnalysisException(f"No data found for period starting from {start_date}")
        
        # Find the last period (closest to but not exceeding end_date)
        end_period = None
        for period in reversed(periods):
            if period.date() <= end_date:
                end_period = period
                break
        
        if end_period is None:
            raise AnalysisException(f"No data found for period ending at {end_date}")
        
        # Calculate average freight charge for start and end periods
        start_charges = [record.freight_charge for record in grouped_data[start_period]]
        end_charges = [record.freight_charge for record in grouped_data[end_period]]
        
        if not start_charges or not end_charges:
            raise AnalysisException("Insufficient data for price movement calculation")
        
        # Calculate average values
        start_value = sum(Decimal(str(charge)) for charge in start_charges) / len(start_charges)
        end_value = sum(Decimal(str(charge)) for charge in end_charges) / len(end_charges)
        
        # Calculate absolute and percentage changes
        absolute_change = calculate_absolute_change(start_value, end_value)
        percentage_change = calculate_percentage_change(start_value, end_value)
        
        # Determine trend direction
        trend_direction = determine_trend_direction(percentage_change)
        
        # Compile results
        result = {
            'start_value': start_value,
            'end_value': end_value,
            'absolute_change': absolute_change,
            'percentage_change': percentage_change,
            'trend_direction': trend_direction
        }
        
        logger.info(f"Calculated price movement: {percentage_change}% change " +
                   f"({absolute_change} absolute), trend: {trend_direction.name}")
        return result
        
    except Exception as e:
        if isinstance(e, AnalysisException):
            raise
        logger.error(f"Error calculating price movement: {str(e)}", exc_info=True)
        raise AnalysisException(f"Failed to calculate price movement: {str(e)}")


def calculate_aggregates(grouped_data: Dict[datetime.datetime, List[FreightData]]) -> dict:
    """
    Calculates statistical aggregates for freight data.
    
    Args:
        grouped_data: Dictionary mapping time periods to lists of FreightData objects
        
    Returns:
        Dictionary containing aggregated metrics for start and end periods
        
    Raises:
        AnalysisException: If calculation fails
    """
    try:
        if not grouped_data:
            raise AnalysisException("No data available for aggregate calculation")
        
        # Sort periods by date
        periods = sorted(grouped_data.keys())
        
        if len(periods) < 2:
            raise AnalysisException("Insufficient data for aggregate calculation (need at least two periods)")
        
        # Get start and end periods
        start_period = periods[0]
        end_period = periods[-1]
        
        # Initialize dictionaries for aggregates
        start_aggregates = {}
        end_aggregates = {}
        
        # Calculate aggregates for start period
        start_charges = [Decimal(str(record.freight_charge)) for record in grouped_data[start_period]]
        if start_charges:
            start_aggregates['average'] = sum(start_charges) / len(start_charges)
            start_aggregates['minimum'] = min(start_charges)
            start_aggregates['maximum'] = max(start_charges)
        
        # Calculate aggregates for end period
        end_charges = [Decimal(str(record.freight_charge)) for record in grouped_data[end_period]]
        if end_charges:
            end_aggregates['average'] = sum(end_charges) / len(end_charges)
            end_aggregates['minimum'] = min(end_charges)
            end_aggregates['maximum'] = max(end_charges)
        
        # Compile results
        result = {
            'start_period': start_aggregates,
            'end_period': end_aggregates
        }
        
        logger.debug(f"Calculated aggregates for {len(grouped_data)} time periods")
        return result
        
    except Exception as e:
        if isinstance(e, AnalysisException):
            raise
        logger.error(f"Error calculating aggregates: {str(e)}", exc_info=True)
        raise AnalysisException(f"Failed to calculate aggregates: {str(e)}")


def compare_with_baseline(current_results: dict, baseline_results: dict) -> dict:
    """
    Compares current analysis results with a baseline period.
    
    Args:
        current_results: Dictionary containing current analysis results
        baseline_results: Dictionary containing baseline analysis results
        
    Returns:
        Dictionary containing comparison metrics
        
    Raises:
        AnalysisException: If comparison fails
    """
    try:
        if not current_results or not baseline_results:
            raise AnalysisException("Missing data for baseline comparison")
        
        # Extract relevant values from both result sets
        current_absolute = current_results.get('absolute_change')
        current_percentage = current_results.get('percentage_change')
        baseline_absolute = baseline_results.get('absolute_change')
        baseline_percentage = baseline_results.get('percentage_change')
        
        if (current_absolute is None or current_percentage is None or 
            baseline_absolute is None or baseline_percentage is None):
            raise AnalysisException("Incomplete data for baseline comparison")
        
        # Convert to Decimal for precise calculation
        current_absolute = Decimal(str(current_absolute))
        current_percentage = Decimal(str(current_percentage))
        baseline_absolute = Decimal(str(baseline_absolute))
        baseline_percentage = Decimal(str(baseline_percentage))
        
        # Calculate differences
        absolute_difference = current_absolute - baseline_absolute
        percentage_difference = current_percentage - baseline_percentage
        
        # Determine if current trend is better or worse than baseline
        # For freight prices, lower is generally better (less cost)
        trend_comparison = "better" if current_percentage < baseline_percentage else "worse"
        if current_percentage == baseline_percentage:
            trend_comparison = "same"
        
        # Compile results
        comparison = {
            'absolute_difference': absolute_difference,
            'percentage_difference': percentage_difference,
            'trend_comparison': trend_comparison
        }
        
        logger.info(f"Baseline comparison: {percentage_difference}% difference " +
                   f"({absolute_difference} absolute), trend: {trend_comparison}")
        return comparison
        
    except Exception as e:
        if isinstance(e, AnalysisException):
            raise
        logger.error(f"Error comparing with baseline: {str(e)}", exc_info=True)
        raise AnalysisException(f"Failed to compare with baseline: {str(e)}")


def format_output(results: dict, output_format: OutputFormat) -> Union[dict, str, bytes]:
    """
    Formats analysis results according to the specified output format.
    
    Args:
        results: Dictionary containing analysis results
        output_format: Desired output format from OutputFormat enum
        
    Returns:
        Formatted results in the requested format (dict for JSON, str for CSV/text)
        
    Raises:
        AnalysisException: If formatting fails
    """
    try:
        # JSON format (return the dictionary directly)
        if output_format == OutputFormat.JSON:
            return results
        
        # CSV format
        elif output_format == OutputFormat.CSV:
            # Create a string buffer for CSV output
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = ["Time Period", "Start Value", "End Value", 
                      "Absolute Change", "Percentage Change", "Trend Direction"]
            writer.writerow(headers)
            
            # Write data row
            period_str = f"{results.get('start_date', '')} to {results.get('end_date', '')}"
            start_value = format_currency(results.get('start_value'), results.get('currency_code', 'USD'), False)
            end_value = format_currency(results.get('end_value'), results.get('currency_code', 'USD'), False)
            absolute_change = format_currency(results.get('absolute_change'), results.get('currency_code', 'USD'), False)
            percentage_change = format_percentage(results.get('percentage_change'), include_sign=True)
            trend_direction = results.get('trend_direction', '').capitalize() if results.get('trend_direction') else ''
            
            writer.writerow([period_str, start_value, end_value, absolute_change, 
                           percentage_change, trend_direction])
            
            # Add time series data if available
            if 'time_series' in results and results['time_series']:
                writer.writerow([])  # Empty row as separator
                writer.writerow(["Timestamp", "Value"])
                
                for entry in results['time_series']:
                    timestamp = entry.get('timestamp', '')
                    value = format_currency(entry.get('value'), results.get('currency_code', 'USD'), False)
                    writer.writerow([timestamp, value])
            
            # Return the CSV content
            return output.getvalue()
        
        # Text format (human-readable)
        elif output_format == OutputFormat.TEXT:
            period_str = f"{results.get('start_date', '')} to {results.get('end_date', '')}"
            currency_code = results.get('currency_code', 'USD')
            
            start_value = format_currency(results.get('start_value'), currency_code)
            end_value = format_currency(results.get('end_value'), currency_code)
            absolute_change = format_currency(results.get('absolute_change'), currency_code)
            percentage_change = format_percentage(results.get('percentage_change'), include_sign=True)
            trend_direction = results.get('trend_direction', '').capitalize() if results.get('trend_direction') else ''
            
            # Build text report
            text = [
                "Freight Price Movement Analysis",
                "==============================",
                f"Period: {period_str}",
                f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "SUMMARY:",
                f"Freight charges have {trend_direction.lower()} by {percentage_change} " +
                f"({absolute_change}) over the selected period.",
                "",
                "DETAILS:",
                f"- Starting value: {start_value}",
                f"- Ending value: {end_value}",
                f"- Absolute change: {absolute_change}",
                f"- Percentage change: {percentage_change}",
                f"- Trend direction: {trend_direction}"
            ]
            
            # Add aggregates if available
            if 'aggregates' in results and results['aggregates']:
                text.extend([
                    "",
                    "STATISTICS:"
                ])
                
                start_agg = results['aggregates'].get('start_period', {})
                end_agg = results['aggregates'].get('end_period', {})
                
                if start_agg:
                    text.append("Start Period:")
                    if 'average' in start_agg:
                        text.append(f"  - Average: {format_currency(start_agg['average'], currency_code)}")
                    if 'minimum' in start_agg:
                        text.append(f"  - Minimum: {format_currency(start_agg['minimum'], currency_code)}")
                    if 'maximum' in start_agg:
                        text.append(f"  - Maximum: {format_currency(start_agg['maximum'], currency_code)}")
                
                if end_agg:
                    text.append("End Period:")
                    if 'average' in end_agg:
                        text.append(f"  - Average: {format_currency(end_agg['average'], currency_code)}")
                    if 'minimum' in end_agg:
                        text.append(f"  - Minimum: {format_currency(end_agg['minimum'], currency_code)}")
                    if 'maximum' in end_agg:
                        text.append(f"  - Maximum: {format_currency(end_agg['maximum'], currency_code)}")
            
            # Join all lines with newlines
            return "\n".join(text)
        
        else:
            raise AnalysisException(f"Unsupported output format: {output_format}")
        
    except Exception as e:
        if isinstance(e, AnalysisException):
            raise
        logger.error(f"Error formatting output: {str(e)}", exc_info=True)
        raise AnalysisException(f"Failed to format output: {str(e)}")


def generate_cache_key(time_period_id: uuid.UUID, 
                     parameters: dict, 
                     filters: Optional[List[dict]] = None) -> str:
    """
    Generates a unique cache key for analysis parameters.
    
    Args:
        time_period_id: ID of the time period for analysis
        parameters: Dictionary of analysis parameters
        filters: Optional list of filter dictionaries
        
    Returns:
        Unique cache key string
    """
    try:
        # Create a dictionary with all parameters for consistent serialization
        key_dict = {
            'time_period_id': str(time_period_id),
            'parameters': parameters,
            'filters': filters
        }
        
        # Serialize to JSON and compute hash
        json_str = json.dumps(key_dict, sort_keys=True)
        hash_obj = hashlib.md5(json_str.encode('utf-8'))
        key_hash = hash_obj.hexdigest()
        
        # Return the cache key with prefix
        cache_key = f"{CACHE_PREFIX}{key_hash}"
        logger.debug(f"Generated cache key: {cache_key}")
        return cache_key
        
    except Exception as e:
        logger.warning(f"Error generating cache key: {str(e)}")
        # Fallback to a simpler key in case of error
        fallback_key = f"{CACHE_PREFIX}{time_period_id}_{hash(str(parameters))}"
        return fallback_key


def get_cached_result(cache_key: str) -> Optional[dict]:
    """
    Retrieves cached analysis result if available.
    
    Args:
        cache_key: Cache key for the analysis
        
    Returns:
        Cached analysis result or None if not found
    """
    try:
        # Get data from cache
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Deserialize JSON data
            result = json.loads(cached_data)
            logger.info(f"Cache hit for key: {cache_key}")
            return result
        
        logger.debug(f"Cache miss for key: {cache_key}")
        return None
        
    except Exception as e:
        logger.warning(f"Error retrieving from cache: {str(e)}")
        return None


def cache_analysis_result(cache_key: str, result: dict) -> bool:
    """
    Caches analysis result for future use.
    
    Args:
        cache_key: Cache key for the analysis
        result: Analysis result to cache
        
    Returns:
        True if caching was successful, False otherwise
    """
    try:
        # Serialize result to JSON
        json_data = json.dumps(result)
        
        # Store in cache with TTL
        cache.set(cache_key, json_data, CACHE_TTL_SECONDS)
        
        logger.info(f"Cached analysis result with key: {cache_key}")
        return True
        
    except Exception as e:
        logger.error(f"Error caching analysis result: {str(e)}")
        return False


def validate_time_period(time_period: TimePeriod) -> bool:
    """
    Validates a time period for analysis.
    
    Args:
        time_period: TimePeriod instance to validate
        
    Returns:
        True if valid, raises exception otherwise
        
    Raises:
        AnalysisException: If time period is invalid
    """
    if time_period is None:
        raise AnalysisException("Time period cannot be None")
    
    if time_period.start_date is None:
        raise AnalysisException("Time period must have a start date")
    
    if time_period.end_date is None:
        raise AnalysisException("Time period must have an end date")
    
    if time_period.start_date >= time_period.end_date:
        raise AnalysisException("Start date must be before end date")
    
    if time_period.granularity is None:
        raise AnalysisException("Time period must have a granularity")
    
    if time_period.granularity == GranularityType.CUSTOM and not time_period.custom_interval_days:
        raise AnalysisException("Custom granularity requires specifying custom_interval_days")
    
    return True


def validate_analysis_parameters(parameters: dict) -> bool:
    """
    Validates analysis parameters.
    
    Args:
        parameters: Dictionary of analysis parameters
        
    Returns:
        True if valid, raises exception otherwise
        
    Raises:
        AnalysisException: If parameters are invalid
    """
    if not parameters or not isinstance(parameters, dict):
        raise AnalysisException("Analysis parameters must be a non-empty dictionary")
    
    # Check for required parameters
    required_params = ['calculate_absolute_change', 'calculate_percentage_change', 'identify_trend_direction']
    for param in required_params:
        if param not in parameters:
            raise AnalysisException(f"Missing required parameter: {param}")
    
    # Validate output format if specified
    if 'output_format' in parameters:
        output_format = parameters['output_format']
        if output_format not in [format.name for format in OutputFormat]:
            raise AnalysisException(f"Invalid output format: {output_format}")
    
    # Validate compare_to_baseline parameters if enabled
    if parameters.get('compare_to_baseline'):
        if 'baseline_period_id' not in parameters:
            raise AnalysisException("Baseline comparison requires baseline_period_id")
    
    # Validate custom interval if specified
    if 'custom_interval' in parameters:
        custom_interval = parameters['custom_interval']
        try:
            interval_days = int(custom_interval)
            if interval_days <= 0:
                raise AnalysisException("Custom interval must be a positive integer")
        except ValueError:
            raise AnalysisException("Custom interval must be a valid integer")
    
    return True


def create_time_series(grouped_data: Dict[datetime.datetime, List[FreightData]]) -> List[dict]:
    """
    Creates a time series representation of freight data.
    
    Args:
        grouped_data: Dictionary mapping time periods to lists of FreightData objects
        
    Returns:
        List of time series data points
        
    Raises:
        AnalysisException: If time series creation fails
    """
    try:
        if not grouped_data:
            return []
        
        time_series = []
        
        # Sort periods by date
        sorted_periods = sorted(grouped_data.keys())
        
        for period in sorted_periods:
            data_points = grouped_data[period]
            
            if data_points:
                # Calculate average freight charge for this period
                charges = [Decimal(str(record.freight_charge)) for record in data_points]
                average_charge = sum(charges) / len(charges)
                
                # Create data point
                data_point = {
                    'timestamp': period.isoformat(),
                    'value': average_charge,
                    'data_points': len(charges)
                }
                
                time_series.append(data_point)
        
        logger.debug(f"Created time series with {len(time_series)} data points")
        return time_series
        
    except Exception as e:
        logger.error(f"Error creating time series: {str(e)}", exc_info=True)
        raise AnalysisException(f"Failed to create time series: {str(e)}")